# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate02.c

Purpose: Legacy negative `fallocate()` test for `EBADF`, `EINVAL`, and large-offset `EFBIG` cases.

Important APIs/types/functions: `fallocate`, read-only and writable fds, `DEFAULT_TEST_MODE`, `TST_ABI64`/`_FILE_OFFSET_BITS`, `LLONG_MAX`, and old LTP result macros.

Control flow: `setup()` creates a read-only and read-write file and writes 12 blocks to the writable one. The table tries read-only fd, negative offset/len, zero length, too-negative offset, and optional huge offset/len cases, checking errno.

State and persistence behavior: Persistent state is the prepared tmpdir files and fd permissions. No successful allocation is expected.

Dependencies and integration points: Build-time ABI macros determine whether huge-file cases are included.

Risks and test signals: The test compares `TEST_ERRNO` directly, so a syscall returning success with stale errno would be suspicious. Unsupported filesystems become `TCONF`.
