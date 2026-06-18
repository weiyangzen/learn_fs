<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba3dump -->
# sources/user-network-fs/samba/source4/scripting/bin/samba3dump

## Purpose

`samba3dump` inspects and prints data from a Samba3-style lib/private directory, either as a summary or detailed dump.

## Important APIs, Types, and Functions

Printing helpers include `print_header()`, `print_samba3_policy()`, `print_samba3_sam()`, `print_samba3_shares()`, `print_samba3_secrets()`, `print_samba3_regdb()`, `print_samba3_winsdb()`, `print_samba3_groupmappings()`, `print_samba3_aliases()`, `print_samba3_idmapdb()`, `print_samba3()`, and `print_samba3_summary()`.

## Control Flow

The script parses `--format` as `summary` or `full`, expects a libdir and optional smb.conf, creates a Samba3 parameter context with private/state/lock directories set to libdir, loads smb.conf, opens `samba.samba3.Samba3`, and prints either counts or full policy/WINS/registry/secrets/idmap/SAM/group/share data.

## State and Persistence Behavior

It is read-only but can print sensitive secrets, including stored plaintext machine passwords and LDAP bind passwords.

## Dependencies and Integration Points

It depends on Samba3 Python bindings, Samba3 passdb/registry/WINS/idmap readers, and LSA SID name constants.

## Risks and Edge Cases

There appears to be an argument bug: the optional smb.conf branch checks `len(args) < 1` after already requiring at least one argument, so a second argument may be ignored and `libdir/smb.conf` used. Full output leaks secrets to stdout.

## Test Signals

Tests should cover summary and full output against fixture Samba3 directories, optional smb.conf behavior, empty databases, secret redaction expectations if added, and invalid format/argument handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba3dump -->
