## sources/user-network-fs/samba/source3/lib/substitute_generic.c

Purpose: generic allocated-string substitution helpers used by `substitute.c` and other Samba utilities. It adapts lower-level `realloc_string_sub_raw` to the historic Samba calling convention that mutates/reallocates a talloc-allocated string.

Important APIs are `realloc_string_sub2` and `realloc_string_sub`. `realloc_string_sub2` accepts options for unsafe-character replacement and trailing-dollar handling; `realloc_string_sub` is the common safe wrapper that removes unsafe shell/path characters and disallows trailing dollar behavior.

Control flow: the function validates non-null/non-empty input, optionally selects `STRING_SUB_UNSAFE_CHARACTERS` and `_` as replacement policy, then calls `realloc_string_sub_raw` with `replace_once=false`. On failure it logs an out-of-memory error and returns `NULL` without touching the caller’s existing pointer, matching the documented odd convention that the string is usually allocated on `talloc_tos`.

State and persistence: no global state. Returned strings remain talloc-owned according to the lower-level realloc helper. Dependencies are `includes.h`, Samba string wrappers, debug logging, and raw substitution logic elsewhere in the tree.

Risks: returning `NULL` for both invalid arguments and allocation failure makes diagnosis caller-dependent. Because the old pointer may still be valid on failure, callers must not overwrite their only reference before checking. Tests should cover repeated replacements, unsafe character filtering, trailing-dollar cases, empty pattern rejection, and preserving the original string on allocation failure paths where injectable alloc failure is available.
