<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.c -->
# sources/user-network-fs/cifs-utils/cifskey.c

## Purpose

`cifskey.c` provides the small keyutils wrapper used by `cifscreds` and `pam_cifscreds` to search, add, and update CIFS logon keys.

## Important APIs, Types, and Functions

The public functions are `key_search` and `key_add`. `key_search` builds a `cifs:<type>:<addr>` description and searches `DEST_KEYRING`. `key_add` builds the same description, formats payload `user:pass`, adds a `logon` key, and optionally sets a timeout.

## Control Flow

Callers resolve an address or domain first, then call `key_search` to detect existing credentials or `key_add` to create/replace them. Both functions validate that formatted strings fit fixed buffers.

## State and Persistence Behavior

Persistent state is stored in the caller's session keyring as keyutils `logon` keys. Payloads contain plaintext `username:password` available only through key permissions.

## Dependencies and Integration Points

It depends on keyutils, `cifskey.h`, and `resolve_host.h` for address size constants. It is shared by the CLI and PAM module.

## Risks and Edge Cases

Description and payload buffers are fixed-size and reject overlong inputs with `EINVAL`. Key permission setting is the caller's responsibility after `key_add`. Password material remains in stack buffers until overwritten naturally.

## Test Signals

Use an isolated keyring to verify search misses/hits, add with and without timeout, overlong user/password/address rejection, and permission setting by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.c -->
