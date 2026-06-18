# sources/user-network-fs/samba/source3/lib/ms_fnmatch.c

## sources/user-network-fs/samba/source3/lib/ms_fnmatch.c

Purpose: Implements Microsoft/SMB filename pattern matching, including DOS wildcard behavior that differs from POSIX `fnmatch`.

Important APIs/types/functions: `ms_fnmatch()` is the public entry point. `ms_fnmatch_core()` recursively matches UCS-2 pattern/name pairs. `null_match()` accepts trailing wildcard-only patterns. `struct max_n` memoizes recursion progress for `*` and `<` wildcards.

Control flow: `ms_fnmatch()` normalizes `..`, fast-paths patterns without SMB wildcards via `strcmp`/`strcasecmp_m`, converts pattern and string to UCS-2, optionally translates legacy `?`, `.*`, and `*.` into Windows-style `>`, `"`, and `<`, allocates recursion guards, and calls the core matcher with the last-dot pointer. The core matcher handles `*`, `<`, `?`, `>`, `"`, literal characters, case folding, and end-of-string success.

State and persistence behavior: No persistent state. Temporary UCS-2 allocations use `talloc_tos()` and wildcard memo state uses stack or heap allocation.

Dependencies and integration points: Used by SMB pathname matching and directory enumeration filters. Depends on Samba charset conversion, wide-character helpers, talloc stack, and SMB wildcard constants.

Risks: Wildcard semantics are compatibility-sensitive, especially last-dot behavior and LANMAN1 fast path. Recursive matching can become expensive without `max_n`. Conversion failure returns mismatch.

Test signals: Filename matching tests should cover `*`, `?`, `<`, `>`, `"`, dot/no-dot names, `..`, case-sensitive and insensitive modes, old-protocol translation, Unicode case folding, and long wildcard-heavy patterns.
