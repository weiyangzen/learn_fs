# File Research: sources/os/linux/linux/fs/lockd/share.h

Purpose: Declares DOS share tracking structures and server-side share operation APIs for lockd.

Key contents:
- Defines synthetic `LOCKD_SHARE_SVID` for lockowner lookup during share operations.
- `struct nlm_share` links a host, file, owner handle, access mode, and deny mode.
- Declares `nlmsvc_share_file()`, `nlmsvc_unshare_file()`, and `nlmsvc_traverse_shares()`.

Dependencies and integration:
- Used by lockd server share implementation and resource traversal/GC.
- Depends on `struct nlm_host`, `struct nlm_file`, and `nlm_host_match_fn_t` from `lockd.h`.

Risk notes:
- Share ownership is represented by XDR netobj owner handles, so comparisons must respect length and data, not C strings.
