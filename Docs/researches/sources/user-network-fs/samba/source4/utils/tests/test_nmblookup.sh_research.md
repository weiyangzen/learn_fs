<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_nmblookup.sh -->
# sources/user-network-fs/samba/source4/utils/tests/test_nmblookup.sh

## Purpose

This shell script runs blackbox `nmblookup` tests against a Samba test environment, checking direct server-IP lookups and ordinary NetBIOS name lookups for server name, NetBIOS name, and NetBIOS alias.

## Important APIs, Types, and Functions

- Positional arguments provide `NETBIOSNAME`, `NETBIOSALIAS`, `SERVER`, `SERVER_IP`, `nmblookup`, and trailing torture options.
- `testit()` prints subtest status, runs a command, increments `failed` on nonzero exit, and returns the command status.

## Control Flow

The script shifts the first five arguments, stores remaining options, runs six `testit` calls, and exits with the accumulated failure count.

## State and Persistence Behavior

No files are written. The only state is the `failed` counter and subprocess exit codes.

## Dependencies and Integration Points

It depends on `/bin/sh`, `expr`, an executable `nmblookup`, and a test environment where the supplied server and aliases are resolvable by WINS/NetBIOS.

## Risks and Edge Cases

Arguments are mostly unquoted in command execution, so spaces or shell metacharacters in names/options would break execution. The failure count is used directly as the exit code.

## Test Signals

Pass signal is exit `0` after all six lookup commands succeed. Any failed lookup increments the exit status and identifies the failing subtest in stdout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_nmblookup.sh -->
