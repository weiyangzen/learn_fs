<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifscreds.c -->
# sources/user-network-fs/cifs-utils/cifscreds.c

## Purpose

`cifscreds.c` implements the `cifscreds` CLI for adding, clearing, clearing all, and updating CIFS username/password logon keys in the caller's session keyring.

## Important APIs, Types, and Functions

Important types are `struct cmdarg` and `struct command`. Major functions are `usage`, `key_search_all`, `cifscreds_add`, `cifscreds_clear`, `cifscreds_clearall`, `cifscreds_update`, `check_session_keyring`, and `main`. It uses `key_search` and `key_add` from `cifskey.c`.

## Control Flow

`main` parses global options `--username`, `--domain`, and `--timeout`, resolves a command by exact or unambiguous prefix, defaults the username from `getusername(getuid())`, checks for a session keyring, then dispatches. Host commands resolve hostnames into one or more addresses; domain mode uses the domain string directly. Add checks for existing keys before prompting via `getpass`, then adds a key per address and sets permissions. Clear unlinks matching keys. Clearall scans the session keyring for descriptions beginning with `cifs:` and unlinks them. Update finds existing matching keys and re-adds payloads with the new password.

## State and Persistence Behavior

The persistent state is the keyutils `logon` key payload in `KEY_SPEC_SESSION_KEYRING`; optional timeouts are set on add. Passwords are held transiently in process memory through `getpass` and key payload strings.

## Dependencies and Integration Points

It depends on keyutils, resolver helpers, `cifskey.h`, `mount.h` exit constants, and utility functions. `pam_cifscreds.c` shares the same key format through `cifskey.c`.

## Risks and Edge Cases

The command parser accepts prefixes and must detect ambiguity. The fixed `addrs[16]` array in update matches resolver limits but depends on `MAX_ADDRESSES` staying 16. Password memory is not explicitly scrubbed in this CLI path. Domain and username disallowed-character checks are important because key descriptions are colon-delimited.

## Test Signals

Tests should cover add/update/clear/clearall against an isolated session keyring, multi-address hosts, domain mode, invalid usernames/domains, duplicate key handling, timeout behavior, missing session keyring warnings, and ambiguous command prefixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifscreds.c -->
