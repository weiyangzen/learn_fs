# File Research: sources/virtualization/libnbd/lib/utils.c

General utility module for debug formatting, string-list copying, socket creation wrappers, fork-safe diagnostics, fork-safe assertion, and custom execvpe support.

Utility functions:
- `nbd_internal_hexdump`: formatted hex/ascii dump.
- `nbd_internal_copy_string_list`: deep-copies null-terminated string lists.
- `nbd_internal_set_argv`: validates and stores command argv on handle.
- `nbd_internal_set_querylist`: copies explicit metadata queries or defaults from requested contexts.
- Printable helpers convert buffers, strings, and string lists into bounded printable forms for API tracing.

Fork-safe diagnostics:
- `nbd_internal_fork_safe_itoa`: integer formatting without stdio allocation.
- `xwritel`: best-effort writev-based list writer intended to remain async-signal-safe.
- `nbd_internal_fork_safe_perror`: fork-safe perror-like diagnostic preserving errno.
- `nbd_internal_fork_safe_assert`: emits assertion failure using fork-safe helpers, then aborts.

Socket wrappers:
- `nbd_internal_socket`: creates close-on-exec and optionally nonblocking sockets, with fallback fcntl path when `SOCK_CLOEXEC` is missing.
- `nbd_internal_socketpair`: close-on-exec socketpair wrapper.

Execvpe implementation:
- `get_path`: copies `PATH`, falling back to `confstr(_CS_PATH)`.
- `nbd_internal_execvpe_init`: precomputes candidate pathnames and allocates shell-fallback argv before fork.
- `nbd_internal_execvpe_uninit`: frees exec context.
- `nbd_internal_fork_safe_execvpe`: child-side async-signal-safe exec loop, retrying nonfatal pathname errors and falling back to `/bin/sh` on `ENOEXEC`.

Interactions:
- Command-based connections use argv and execvpe helpers.
- Tests in `test-fork-safe-assert*` and `test-fork-safe-execvpe*` validate fork-safe paths.

Research notes:
- The execvpe split is intentionally pre-fork allocation plus post-fork exec-only behavior to avoid unsafe library calls in the child.
- Socket close-on-exec fallbacks note unavoidable race on platforms lacking `SOCK_CLOEXEC`.
