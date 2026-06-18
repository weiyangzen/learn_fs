# sources/test-tools/ltp/testcases/kernel/syscalls/fadvise/posix_fadvise04.c

Purpose: Verifies `posix_fadvise()` returns `ESPIPE` when used on a pipe descriptor.

Important APIs/types/functions: `SAFE_PIPE`, `SAFE_CLOSE`, `posix_fadvise(pipedes[0], ...)`, defined advice constants, and `ESPIPE`.

Control flow: `setup()` creates a pipe and closes the write end. Each testcase calls `posix_fadvise` on the read end with one advice and expects `ESPIPE`.

State and persistence behavior: The pipe read fd is the runtime state. No filesystem data is used.

Dependencies and integration points: Complements file and invalid-fd fadvise coverage by exercising non-seekable descriptors.

Risks and test signals: Failure means the syscall accepted or misreported advice on a pipe. Cleanup must not double-close invalid descriptors.
