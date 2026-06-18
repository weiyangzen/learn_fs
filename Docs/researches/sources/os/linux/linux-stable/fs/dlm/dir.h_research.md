# File Research: sources/os/linux/linux-stable/fs/dlm/dir.h

## Purpose
`dir.h` declares the DLM directory API used by locking, recovery, and RCOM code.

## Exports
- `dlm_dir_nodeid(struct dlm_rsb *rsb)`
- `dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)`
- `dlm_recover_dir_nodeid(struct dlm_ls *ls, const struct list_head *root_list)`
- `dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)`
- `dlm_copy_master_names(struct dlm_ls *ls, const char *inbuf, int inlen, char *outbuf, int outlen, int nodeid)`

## Integration
The header depends on `struct dlm_ls` and `struct dlm_rsb` definitions from `dlm_internal.h`. It is used by `lock.c` for resource lookup/master routing and by recovery messaging paths for directory rebuild.
