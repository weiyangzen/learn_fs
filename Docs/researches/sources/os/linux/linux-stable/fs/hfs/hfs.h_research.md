# File Research: sources/os/linux/linux-stable/fs/hfs/hfs.h

## Scope

Small classic HFS header that includes common on-disk declarations and defines directory iteration private state.

## Data Structure

`struct hfs_readdir_data` links an open directory stream into the owning inode's `open_dir_list`, stores the associated `struct file`, and records the last catalog key used for readdir position adjustment during deletion.

## Dependencies And Risks

This structure is used by `dir.c` and `catalog.c` under `open_dir_lock`. Its correctness depends on release removing entries from the list and catalog deletion adjusting `f_pos` when a removed key precedes an active iterator.
