<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dirent.c -->
## sources/test-tools/strace/src/dirent.c

Purpose: Decodes legacy `getdents` and `readdir` directory entry syscalls.

Important APIs and types: `kernel_dirent_t` via mpers, `header_size`, `print_dentry_head`, `decode_dentry_head`, `decode_dentry_tail`, `SYS_FUNC(getdents)`, `print_old_dirent`, and `SYS_FUNC(readdir)`.

Control flow: `getdents` delegates to `xgetdents` with callbacks. The head callback returns each record length and optionally prints `d_ino`, `d_off`, and `d_reclen`. The tail callback prints capped `d_name` and the trailing `d_type` byte. `readdir` prints fd on entry and, on exit, prints either the raw pointer for zero return or one decoded old dirent.

State and persistence: No persistent state, except optional `tcp->last_dirfd` when SELinux context support is enabled.

Dependencies and integration: Depends on `defs.h`, `kernel_dirent.h`, mpers, `xgetdents.h`, `dirent_types`, path printing, and fd printing.

Risks: Record length and name/type packing are kernel ABI-sensitive. Tail decoding caps names at 256 bytes and must avoid overreading malformed records.

Test signals: Tests should include multiple entries, abbreviated output, long names, d_type decoding, malformed/truncated records, zero-return `readdir`, and mpers personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dirent.c -->
