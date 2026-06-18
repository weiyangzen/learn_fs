<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/ktpass.sh -->
# sources/user-network-fs/samba/source4/scripting/bin/ktpass.sh

## Purpose

`ktpass.sh` creates a keytab entry for a Samba principal using `ldbsearch` to discover the principal's key version number and `ktutil` to write the keytab.

## Important APIs, Types, and Functions

Options include `--out`, `--princ`, `--pass`, `--host`, `--ptype`, `--enc`, and `--path-to-ldbsearch`. The `usage()` function prints help. The script queries `msds-keyversionnumber` and drives `ktutil` via a here-document.

## Control Flow

It parses long options with `getopt`, defaults encryption to `rc4-hmac`, resolves an `ldbsearch` path, validates required options, defaults host to `hostname`, searches LDAP using Kerberos, prompts for password if `--pass '*'`, then invokes `ktutil add_entry -password` followed by `wkt`.

## State and Persistence Behavior

It writes the requested keytab file. Password material is held in shell variables and sent to `ktutil` stdin.

## Dependencies and Integration Points

It depends on shell, GNU-style `getopt`, `ldbsearch`, Kerberos authentication, and `ktutil`.

## Risks and Edge Cases

Password on the command line can leak through process listings; prompting disables echo but does not robustly restore terminal settings on interruption. The LDAP filter interpolates the principal directly. `--ptype` is accepted but ignored.

## Test Signals

Tests should cover kvno lookup success/failure, prompted password mode, each encryption value, alternate `ldbsearch` path, missing mandatory options, and keytab validation with `klist -k`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/ktpass.sh -->
