<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-cp.c -->
# sources/user-network-fs/libsmb2/utils/smb2-cp.c

Purpose: Command-line copy utility that copies between local files and SMB URLs in either direction.

Important APIs, types, and functions: Defines `struct file_context`, `usage`, `free_file_context`, `fstat_file`, `file_pread`, `file_pwrite`, `open_file`, global 1 MiB buffer, and `main`.

Control flow: Each operand is opened as local or SMB based on `smb://` prefix. The source is statted, then a loop reads chunks with pread semantics and writes them to the destination until source size is copied.

State and persistence behavior: Maintains per-file context with local fd, SMB context, URL, and SMB file handle. Remote destination is created/truncated when opened for write.

Dependencies and integration points: Depends on synchronous libsmb2 APIs, POSIX file APIs, URL parser, and platform socket init for Windows/AROS. Used by cp tests.

Risks: Local `read`/`write` calls do not handle short writes robustly beyond advancing by written count from read result. `st_blocks` calculation for SMB metadata uses modulo instead of division, likely wrong but not copy-critical. Remote overwrite is unconditional for destination.

Test signals: Covered by basic, valgrind, and socket-error copy tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-cp.c -->
