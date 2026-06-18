# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.c

## Scope

This file contains small transport support helpers for sockaddr sizing, comparison, duplication, and freeing.

## APIs And Behavior

- Static `SA_LEN()` returns the sockaddr storage length for `AF_INET`, `AF_INET6`, and `AF_NETBIOS`, falling back to generic `struct sockaddr` for unknown families.
- `smb_cmp_sockaddr()` compares two sockaddr structures by family-specific length and content.
- `smb_dup_sockaddr()` allocates and copies a sockaddr using the correct family length.
- `smb_free_sockaddr()` frees an address allocated by `smb_dup_sockaddr()`.

## Dependencies

- Used by SMB transport connection logic and potentially future transports.
- Depends on `smb_tran.h`, `smb_conn.h`, and NetBIOS sockaddr definitions.

## Risks And Invariants

- `smb_free_sockaddr()` must receive an address whose length matches `SA_LEN()` or the kmem free size will be wrong.
- Unknown families are debug-logged and treated as generic sockaddr, which is safe only for limited fallback use.
