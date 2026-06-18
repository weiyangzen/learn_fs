# sources/user-network-fs/davfs2/src/util.h

## Purpose
`util.h` provides shared fatal/warning macros and a portability wrapper for canonical path resolution. It is included by davfs mount and unmount helpers for consistent diagnostics and fallback behavior on systems without `canonicalize_file_name()`.

## Important APIs, Types, and Functions
- `ERR(fmt, ...)`: fatal diagnostic macro. If `errno != 0`, it calls `errx(EXIT_FAILURE, ...)`; otherwise it writes to stderr and exits.
- `WARN(fmt, ...)`: warning macro. If `errno != 0`, it calls `warnx(...)`; otherwise it writes to stdout.
- `ERR_AT_LINE(filename, lineno, fmt, ...)`: uses GNU `error_at_line()` when available, otherwise prints filename/line and exits.
- `mcanonicalize_file_name(path)`: maps to `canonicalize_file_name` when present, otherwise inline fallback using `realpath()` and `strdup()`.

## Control Flow
The macros immediately emit diagnostics and, for `ERR` and `ERR_AT_LINE`, terminate the process. The canonicalization fallback copies the input into a fixed `PATH_MAX` buffer, calls `realpath(path, buf)`, returns `NULL` on failure, and duplicates the resolved path on success.

## State and Persistence
No persistent state is held. Behavior depends on global `errno`, which callers do not always reset before invoking the macros. Returned canonical paths are heap-allocated and caller-owned.

## Dependencies and Integration Points
The header includes `config.h`, libc headers, locale/error handling headers, `err.h`, and optionally GNU `error.h`. It is used by setuid helpers where fatal errors intentionally stop startup/unmount. Its path wrapper is the normalization primitive for mountpoints, fstab entries, secrets keys that are paths, and unmount pidfile derivation.

## Risks and Edge Cases
`ERR` and `WARN` branch on the current global `errno`, but then call `errx`/`warnx`, which do not append errno text; this may be intentional but is surprising because `errno != 0` does not produce `perror`-style output. Because callers may not clear `errno`, unrelated prior errors can alter diagnostics. The fallback `mcanonicalize_file_name()` uses `realpath(path, buf)` after copying into `buf`; the initial `snprintf` is unnecessary. It requires the target to exist, matching `realpath()` behavior.

## Test Signals
Tests should check diagnostics with `errno` set and clear, `ERR_AT_LINE` formatting on systems with and without GNU `error.h`, and canonicalization success/failure for existing, missing, relative, and overlong paths. Callers should be reviewed for stale `errno` before `WARN`/`ERR`.
