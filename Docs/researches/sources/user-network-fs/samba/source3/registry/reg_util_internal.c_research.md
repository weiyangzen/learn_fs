<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.c -->
# sources/user-network-fs/samba/source3/registry/reg_util_internal.c

Purpose: Supplies small internal registry path helpers for splitting and normalizing virtual registry key paths.

Important APIs, types, and functions: `reg_split_path()` splits a mutable path at the first backslash into a base hive and remaining path. `reg_split_key()` splits a mutable path at the last backslash into parent path and leaf key. `normalize_reg_path()` strips leading and trailing backslashes and uppercases the key into a talloc allocation. `reg_remaining_path()` duplicates a key and returns a pointer past the first component.

Control flow: The split functions mutate the input string by replacing a delimiter with `'\0'` and return pointers into that same buffer. Normalization advances over leading delimiters, duplicates the remaining string, repeatedly removes trailing delimiters, then calls `strupper_m()`. `reg_remaining_path()` duplicates the source string and returns either the duplicate itself or the character after the first backslash.

State and persistence behavior: No global state. Split outputs alias caller storage. Normalization and remaining-path outputs are talloc-owned by the supplied context; `reg_remaining_path()` returns an interior pointer into the allocated duplicate, so the talloc allocation must remain alive.

Dependencies and integration points: Depends on Samba talloc, multibyte uppercase conversion, and registry frontend code that needs normalized database keys. It is paired with `reg_util_internal.h`.

Risks: The split helpers destructively edit their input and do not duplicate data. `normalize_reg_path()` assumes `keyname` is non-NULL and dereferences it immediately. `reg_remaining_path()` returns an interior pointer, which can make ownership unclear and can leak the hidden base pointer if callers do not keep the talloc context.

Test signals: Cover NULL and empty inputs, paths without backslashes, leading/trailing repeated backslashes, multibyte uppercase failure, first-vs-last delimiter behavior, and ownership lifetime of the interior pointer returned by `reg_remaining_path()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_internal.c -->
