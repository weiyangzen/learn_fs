<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_samba_tool.sh -->
# sources/user-network-fs/samba/source4/utils/tests/test_samba_tool.sh

## Purpose

This shell script runs blackbox tests for `samba-tool` and machine-account `smbclient` login behavior in a Samba test environment.

## Important APIs, Types, and Functions

- Positional arguments provide server, server IP, username, password, domain, and `smbclient`.
- Environment variables `BINDIR`, `VALGRIND`, `PYTHON`, and `CONFIGURATION` control command locations/wrappers.
- `testit()` runs commands and accumulates failures.

## Control Flow

After argument setup, it derives `$samba_tool` from `$BINDIR/samba-tool`, runs machine-pass `smbclient` login without explicit Kerberos, machine-pass login with `-k`, `samba-tool time`, `domain level show`, `domain info`, and `fsmo show`, then exits with the failure count.

## State and Persistence Behavior

No local files are written by the script. The commands query live Samba services and may use credentials, machine account secrets, and configuration paths provided by the environment.

## Dependencies and Integration Points

It integrates the Python `samba-tool` command, `smbclient`, Samba test configuration, and optional valgrind wrapping. The script expects `$BINDIR` and `$CONFIGURATION` to be set by the test harness.

## Risks and Edge Cases

Commands and many variables are unquoted in command position. The script uses older `smbclient -k` Kerberos syntax, while other tests use `--use-kerberos`. `domain level show` and `fsmo show` do not pass explicit credentials in this script, relying on configuration/environment defaults.

## Test Signals

Pass signal is successful machine-pass SMB access in both auth modes and successful `samba-tool` time/domain/FSMO queries. Failures point to credentials, Kerberos, tool discovery, domain controller reachability, or Samba-tool regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/tests/test_samba_tool.sh -->
