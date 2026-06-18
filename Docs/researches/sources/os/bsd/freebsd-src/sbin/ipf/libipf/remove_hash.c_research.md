# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hash.c

Hash lookup-table removal helper.

Key behavior:
- Builds `IPLT_HASH` lookup operation from an `iphtable_t`.
- Handles anonymous hash names.
- Calls `SIOCLOOKUPDELTABLE`.

Research notes:
- `op.iplo_arg` is only assigned in the anonymous case; otherwise it is left uninitialized.
