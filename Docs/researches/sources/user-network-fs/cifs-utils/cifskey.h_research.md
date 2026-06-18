<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.h -->
# sources/user-network-fs/cifs-utils/cifskey.h

## Purpose

`cifskey.h` defines the CIFS credential key format, size limits, validation character sets, destination keyring, permissions, default timeout, and key helper prototypes.

## Important APIs, Types, and Functions

Key definitions are `KEY_PREFIX`, `MAX_USERNAME_SIZE`, `MOUNT_PASSWD_SIZE`, `MAX_DOMAIN_SIZE`, `USER_DISALLOWED_CHARS`, `DOMAIN_DISALLOWED_CHARS`, `DEST_KEYRING`, `CIFS_KEY_TYPE`, `CIFS_KEY_PERMS`, `DEFAULT_KEY_TIMEOUT`, `key_search`, and `key_add`.

## Control Flow

There is no executable flow; callers include the header and use the constants to validate inputs and call the key helper functions.

## State and Persistence Behavior

The constants define session-keyring persistence and permissions for stored credential keys.

## Dependencies and Integration Points

It requires keyutils types and is used by `cifscreds.c`, `cifskey.c`, and `pam_cifscreds.c`.

## Risks and Edge Cases

The limits here are smaller than the mount helper's credential limits, so PAM/CLI stashed credentials may reject inputs that mount options can carry. Any change to `KEY_PREFIX` or description format breaks key lookup compatibility.

## Test Signals

Compile tests plus keyring integration tests should verify constants match caller behavior and key permissions remain restrictive enough for logon-key payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.h -->
