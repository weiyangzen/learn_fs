# sources/test-tools/fio/oslib/statx.c

Purpose: fallback `statx()` wrapper for systems where libc lacks `statx()`.

Important APIs/functions: under `!CONFIG_HAVE_STATX`, defines `statx()`. If `CONFIG_HAVE_STATX_SYSCALL` is available, it calls `syscall(__NR_statx, ...)`; otherwise it sets `errno = EINVAL` and returns `-1`.

Control flow and state: compile-time selected; no persistent state.

Dependencies and integration: paired with `statx.h`; allows fio code to use a uniform `statx()` symbol where direct syscall support exists.

Risks: on systems without syscall support the fallback fails with `EINVAL`, so callers must handle absence. It does not emulate `statx()` with `stat()`.

Test signals: build on libc-with-statx, syscall-only, and no-statx systems; verify callers degrade gracefully.
