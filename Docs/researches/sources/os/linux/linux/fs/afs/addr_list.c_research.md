# File Research: sources/os/linux/linux/fs/afs/addr_list.c

Purpose: manages AFS server address lists, parses textual/DNS-provided addresses, merges RxRPC peers, and associates peers with server records.

Key interfaces:
- `afs_alloc_addrlist()`, `afs_get_addrlist()`, `afs_put_addrlist()`.
- `afs_parse_text_addrs()`: parses delimited IPv4/IPv6 address lists with optional `+port`.
- `afs_dns_query()`: resolves VL server addresses through DNS.
- `afs_merge_fs_addr4()` and `afs_merge_fs_addr6()`.
- `afs_set_peer_appdata()`.

Implementation notes:
- Address lists are flex-array allocations capped at `AFS_MAX_ADDRESSES`, refcounted, and freed by RCU.
- Peer references are released on final free.
- Parser supports bracketed IPv6, delimiter normalization for colon/comma cases, duplicate delimiters, and port validation.
- DNS results are interpreted either as SRV-style data for `afs_extract_vlserver_list()` or as text address lists.
- IPv4 peers are kept before IPv6 peers; within each family, insertion order is sorted by `rxrpc_peer *` pointer.
- `afs_set_peer_appdata()` diffs old/new sorted lists to set or clear server pointers in RxRPC peer appdata.

Dependencies:
- RxRPC peer lookup/refcounting, DNS resolver, VL server list allocation, and AFS/YFS service port constants.

Edge cases:
- Empty address lists return `-EDESTADDRREQ`.
- Invalid syntax returns `-EINVAL` with trace/debug problem labels.
- When the list is full, additional addresses are silently ignored by merge functions.
