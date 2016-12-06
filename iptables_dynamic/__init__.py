"""
iptables-dynamic is a command line script that helps to dynamically save and
restore iptables rules for some chain(s)
"""

from __future__ import absolute_import, division, print_function
from subprocess import Popen as popen
import argparse
import os


__license__ = "BSD 3-clause"
__copyright__ = "Copyright 2016, Regents of the University of California"
__author__ = "Alireza Rafiei"

"""
A dictionary of default configs.
    rules_dir       will be used by dir_handler. Must be an absolute path for a
                    directory that can be created.
"""
Config = {"rules_dir": "/etc/iptables"}


def dir_handler():
    """
    Checks/Creates the needed directory.

    Returns
    -------
    rules_dir       str
    """
    rules_dir = Config["rules_dir"]
    if not os.access(rules_dir, os.W_OK):
        raise IOError(
            "{} is either invalid or inaccessible".format(rules_dir))
    if not os.path.exists(rules_dir):
        os.makedirs(rules_dir)
    return rules_dir


def table_handler():
    """
    The function which parses the output of iptables_save system command to
    derive tables and modify them.

    Returns
    -------
    derive_tables       function
                        [str] -> [[str]]
    filter_tables       function
                        ([[str]] x [str]) -> [[str]]
    """
    def derive_tables(iptables_save_lines):
        """
        Receives the lines of the iptable_save config file and outputs a list
        containing of tables. Tables are themselves lists of strings where the
        strings are individual lines.

        Arguments
        ---------
        iptables_save_lines [str]

        Returns
        -------
        unique_tables       [[str]]
        """
        table_indices = [
            index
            for index, x in enumerate(iptables_save_lines)
            if '*' in x
        ]
        intervals = list(set(table_indices + [len(iptables_save_lines)]))
        intervals = sorted(intervals)
        tables = [iptables_save_lines[intervals[i]: intervals[i + 1]]
                  for i in xrange(len(intervals) - 1)]
        # Making sure all the rules withing each table are unique
        unique_tables = [
            [table[i] for i in xrange(len(table)) if i == table.index(table[i])]
            for table in tables
        ]
        return unique_tables

    def filter_tables(tables, chains):
        """
        Filters the table to contain only the necessary config for preserving
        the desired chains

        Arguments
        ---------
        tables                              [[str]]
        chains                              [str]

        Retruns
        -------
        filtered_tables_stripped_of_empty   [[str]]
        """
        # A table decleration starts with `*` and ends with `COMMIT`. So the
        # saved rules file must have these two string.
        basic_acceptables = ["*", "COMMIT"]
        chain_acceptables = ([x.upper() for x in chains] +
                             [x.lower() for x in chains])
        acceptables = basic_acceptables + chain_acceptables
        # Checking whether any lines of the file contains an element in
        # `acceptable`. If so, that line is necessary for the execution of the
        # file or is needed by the script to preserve the desired chains.
        tables_with_filtered_chains = [
            filter(lambda x: any([(y in x) for y in acceptables]), table)
            for table in tables]
        # Almost always a table would exist such that no containing chain or
        # rule should be preserved. We'll remove them.
        filtered_tables_stripped_of_empty = []
        for table in tables_with_filtered_chains:
            for line in table:
                if any([(y in line) for y in chain_acceptables]):
                    filtered_tables_stripped_of_empty.append(table)
                    break
        # Warns if the specified chain was not in the rule file.
        for chain in chains:
            chain_found = False
            for table in filtered_tables_stripped_of_empty:
                for line in table:
                    if chain.lower() in line or chain.upper() in line:
                        chain_found = True
                        break
                if chain_found:
                    break
            if not chain_found:
                print("The chain {} was not found".format(chain))
        return filtered_tables_stripped_of_empty

    return derive_tables, filter_tables


def command_handler():
    """
    The main interface for commands.

    Returns
    -------
    save_command        function
                        (str x [str] x bool)
    restore_command     function
                        (str x bool)
    """

    # Used to properly append the ip version to the prefix of the rules files.
    version_prefix = lambda ipv6: "6" if ipv6 else "4"

    def save_command(rules_dir, chains, ipv6):
        """
        Saves the current iptables rules for the desired chains

        Arguments
        ---------
        rules_dir   str
        chains      [str]
                    List of chains to preserve
        ipv6        bool
        """
        derive_tables, filter_tables = table_handler()
        temp_abs_path = "{}/temp.v{}".format(rules_dir, version_prefix(ipv6))
        rules_abs_path = "{}/rules.v{}".format(rules_dir, version_prefix(ipv6))
        popen("ip{}tables-save > {}".format("6" * ipv6, temp_abs_path),
              shell=True, universal_newlines=True).communicate()
        with open(temp_abs_path, "r") as temp:
            lines = temp.readlines()
            tables = filter_tables(derive_tables(lines), chains)
            rules_lines = reduce(lambda x, y: x + y, tables)
            with open(rules_abs_path, 'w') as rules:
                rules.writelines(rules_lines)
        if os.path.exists(rules_abs_path):
            os.remove(temp_abs_path)

    def restore_command(rules_dir, ipv6):
        """
        Restores the current iptables rules for the desired chains

        Arguments
        ---------
        rules_dir   str
        ipv6        bool
        """
        rules_abs_path = "{}/rules.v{}".format(rules_dir, version_prefix(ipv6))
        if os.path.exists(rules_abs_path):
            popen("ip{}tables-restore -n < {}".format("6" * ipv6,
                                                      rules_abs_path),
                  shell=True, universal_newlines=True).communicate()

    return save_command, restore_command,


def argument_handler():
    """
    Function used to parse arguments passed into the script.

    Returns
    -------
    args.start      bool
                    Switch for starting the systemd service
                    - True if selected
                    - False otherwise
    args.stop       bool
                    Switch for stopping the systemd service
                    - True if selected
                    - False otherwise
    args.reload     bool
                    Switch for reloading the systemd service
                    - True if selected
                    - False otherwise
    args.chains     [str]
                    List of chains to preserve

    Raises
    ------
    Exception       If user tries to restore a rule file based on new chains.
                    The intended use case is to selectively save a rule file
                    based on an arbitrary chain and restore the save version
                    in its entirety.
    Exception       If user tries to save a rule file but doesn't spacify at
                    least one chain.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--chains",
                        help="Do further operations for which chains?",
                        nargs='+')
    arg_group = parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument("-s", "--save",
                           help="Save the rules for the desired chains",
                           action='store_true')
    arg_group.add_argument("-r", "--restore",
                           help="Restore the rules", action='store_true')
    args = parser.parse_args()
    if args.restore and args.chains:
        raise Exception("Can't selectively restore a rule file. You should " +
                        "instead selectively save a rule file and restore it" +
                        " in its entirety.")
    if args.save and not args.chains:
        raise Exception("Must choose a chain to selectivly save the rules. " +
                        "Use regular iptables-save if no specific is needed " +
                        "to be saved")
    return (args.save, args.restore, args.chains)


def iptables_dynamic(ipv6=False):
    """
    The main script that'll be called from the command line.

    Parameters
    ----------
    ipv6        bool
    """
    (service_save, service_restore, chains) = argument_handler()
    save_command, restore_command = command_handler()
    rules_dir = dir_handler()
    if service_restore:
        restore_command(rules_dir, ipv6)
    elif service_save:
        save_command(rules_dir, chains, ipv6)


def ip6tables_dynamic():
    """
    Decorated version of `iptables_dynamic` for ipv6 so that script naming
    follows the iptables convention (i.e. iptables for v4 and ip6tables for v6
    etc.)
    """
    return iptables_dynamic(ipv6=True)
