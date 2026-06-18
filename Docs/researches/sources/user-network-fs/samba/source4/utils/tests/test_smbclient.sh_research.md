<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_smbclient.sh -->
# sources/user-network-fs/samba/source4/utils/tests/test_smbclient.sh

## Purpose

This shell script blackbox-tests `smbclient` machine-account authentication to the `tmp` share with Kerberos disabled and required.

## Important APIs, Types, and Functions

- Positional arguments supply server, server IP, username, password, domain, and `smbclient`; only server and smbclient are used.
- `testit()` runs a subcommand, prints success/failure, and increments `failed`.

## Control Flow

The script runs two `smbclient -c 'ls' //$SERVER/tmp --machine-pass` commands: one with `--use-kerberos=disabled`, one with `--use-kerberos=required`. It exits with the number of failed subtests.

## State and Persistence Behavior

No files are written. The test reads the remote `tmp` share directory and uses the local machine account secret through Samba configuration.

## Dependencies and Integration Points

It depends on the test harness setting `CONFIGURATION` and optional `VALGRIND`, a usable `smbclient`, and a server exposing `tmp` to the machine account.

## Risks and Edge Cases

Unused positional variables are accepted for harness consistency. Variables are unquoted in command execution, so unusual server names or configuration strings can break the shell command.

## Test Signals

Exit `0` means both non-Kerberos and required-Kerberos machine-pass SMB sessions listed the share successfully. Nonzero exit identifies one or both authentication modes as broken.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_smbclient.sh -->
