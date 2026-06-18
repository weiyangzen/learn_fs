# File Research: sources/os/linux/linux/fs/ocfs2/dir.h

## Purpose
Public internal header for OCFS2 directory manipulation.

## Key Structures
`struct ocfs2_dx_hinfo` stores directory-name hash results:
- `major_hash`
- `minor_hash`

`struct ocfs2_dir_lookup_result` is the shared lookup/preparation context for directory operations. It can hold:
- unindexed leaf buffer and dirent
- dx root buffer
- dx leaf buffer and dx entry
- computed hash info
- previous free-list leaf buffer for indexed free-space maintenance.

## Declared Operations
- lookup/free:
  - `ocfs2_find_entry()`
  - `ocfs2_free_dir_lookup_result()`
- mutation:
  - `ocfs2_delete_entry()`
  - `__ocfs2_add_entry()`
  - inline wrapper `ocfs2_add_entry()`
  - `ocfs2_update_entry()`
- checks:
  - `ocfs2_check_dir_for_entry()`
  - `ocfs2_empty_dir()`
- name-to-inode lookup:
  - `ocfs2_find_files_on_disk()`
  - `ocfs2_lookup_ino_from_name()`
- iteration:
  - `ocfs2_readdir()`
  - `ocfs2_dir_foreach()`
- insertion preparation:
  - `ocfs2_prepare_dir_for_insert()`
- creation/truncation:
  - `ocfs2_fill_new_dir()`
  - `ocfs2_dx_dir_truncate()`
- trailer utility:
  - `ocfs2_dir_trailer_from_size()`
