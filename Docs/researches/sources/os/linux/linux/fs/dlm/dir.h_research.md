# File Research: sources/os/linux/linux/fs/dlm/dir.h

## Role

`dir.h` is the public internal header for the DLM resource-directory implementation in `dir.c`.

## Exposed Functions

- `dlm_dir_nodeid(struct dlm_rsb *rsb)`: returns the directory owner cached in an RSB.
- `dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)`: maps a resource hash to a member nodeid using lockspace membership weighting.
- `dlm_recover_dir_nodeid(struct dlm_ls *ls, const struct list_head *root_list)`: recomputes directory owners for a recovery root list.
- `dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)`: rebuilds directory entries during recovery.
- `dlm_copy_master_names(struct dlm_ls *ls, const char *inbuf, int inlen, char *outbuf, int outlen, int nodeid)`: fills an RCOM response buffer with resource names mastered locally and directed to the requesting directory node.

## Dependencies and Consumers

The header forward-relies on core structures from `dlm_internal.h`, so users include `dlm_internal.h` first. It is consumed by `lock.c`, `recover.c`/recovery code, and `dir.c` itself to route master lookup, recovery, and resource cleanup behavior.

## Research Notes

The small header boundary is clean: all directory details, including dump contexts and recovery parsing, remain private to `dir.c`; other files only see the directory node mapping and recovery entry points.
