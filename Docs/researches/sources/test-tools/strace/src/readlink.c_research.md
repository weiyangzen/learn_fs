# sources/test-tools/strace/src/readlink.c

Purpose: Decodes `readlink`, `readlinkat`, and variants that return path text into a user buffer.

Important APIs/types/functions: syscall decoder functions for readlink-like syscalls.

Control flow: prints input path arguments on entry. On exit, if successful, prints the output buffer as a string limited by return value and buffer size; on error it prints the buffer address. `readlinkat` also prints directory fd.

State and persistence: stateless; output rendering depends on `tcp->u_rval`.

Dependencies/integration: path printers, fd printers, string-buffer output helpers, and syscall phase/error helpers.

Risks: return value is not NUL-terminated path length, so the decoder must not over-read. Empty successful links and truncated outputs need distinct rendering from errors.

Test signals: readlink/readlinkat success, ENOENT, small buffer truncation, empty target, and invalid output pointer.
