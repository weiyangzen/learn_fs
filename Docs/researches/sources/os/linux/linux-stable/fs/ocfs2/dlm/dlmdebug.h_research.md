# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.h

## Purpose

`dlmdebug.h` declares DLM debug helpers and provides debugfs setup/teardown APIs, with no-op stubs when `CONFIG_DEBUG_FS` is disabled.

## API

Always declared:

- `dlm_print_one_mle(struct dlm_master_list_entry *mle)`

With `CONFIG_DEBUG_FS`:

- `struct debug_lockres`
- `dlm_debug_init(struct dlm_ctxt *dlm)`
- `dlm_create_debugfs_subroot(struct dlm_ctxt *dlm)`
- `dlm_destroy_debugfs_subroot(struct dlm_ctxt *dlm)`
- `dlm_create_debugfs_root(void)`
- `dlm_destroy_debugfs_root(void)`

Without debugfs, the setup and teardown functions compile as empty inline stubs.

## Role In The DLM

This header lets domain setup and teardown call debugfs functions unconditionally while preserving builds without debugfs support.
