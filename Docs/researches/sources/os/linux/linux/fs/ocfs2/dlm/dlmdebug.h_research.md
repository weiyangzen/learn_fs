# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.h

## Purpose
Declares OCFS2 DLM debug helpers and debugfs lifecycle hooks.

## Exposed API
- Always declares `dlm_print_one_mle()`.
- Under `CONFIG_DEBUG_FS`, declares `struct debug_lockres` and debugfs init/create/destroy functions.
- Without `CONFIG_DEBUG_FS`, provides empty inline replacements for debugfs lifecycle calls.

## Notes
This isolates debugfs conditional compilation from the rest of the DLM domain code. Callers can invoke debug initialization and teardown unconditionally.
