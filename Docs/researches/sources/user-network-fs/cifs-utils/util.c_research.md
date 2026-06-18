# sources/user-network-fs/cifs-utils/util.c

## Purpose
`util.c` provides small portability helpers for cifs-utils code paths that do not link Samba's libreplace: fallback `strlcpy`, fallback `strlcat`, and UID-to-username lookup.

## Important APIs and functions
When configure does not provide `HAVE_STRLCPY` or `HAVE_STRLCAT`, this file defines compatible `strlcpy` and `strlcat`. `getusername(uid_t uid)` wraps `getpwuid` and returns the passwd entry's `pw_name` pointer or `NULL`.

## Control flow
The string functions compute source/destination lengths, copy only what fits, always NUL-terminate when buffer size permits, and return the length that would have resulted. `getusername` performs a single passwd database lookup.

## State and persistence behavior
No persistent state is written. `getusername` returns a pointer owned by libc's passwd storage, which may be overwritten by later passwd calls.

## Dependencies and integration points
It depends on `<string.h>`, `<pwd.h>`, and `<sys/types.h>`, and exposes declarations through `util.h`. It is a portability layer shared by cifs-utils programs.

## Risks
`strlcpy` uses `if (bufsize <= 0)` even though `bufsize` is `size_t`; harmless but stylistically misleading. `getusername` comments "caller frees username if necessary", but the returned `pw_name` must not be freed, which can mislead callers. These replacements should match platform semantics exactly to avoid truncation bugs.

## Test signals
Unit-test truncation, zero-size buffers, exact-fit buffers, empty strings, overlapping assumptions, and return lengths against known `strlcpy`/`strlcat` behavior. Test `getusername` for existing and nonexistent UIDs without freeing the returned pointer.
