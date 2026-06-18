# sources/security-integrity/selinux/libselinux/src/is_customizable_type.c

Purpose: Determines whether a context's type appears in the policy's customizable types list.

Important APIs/types/functions: `is_context_customizable()` parses the input context and compares its type to a lazily loaded global `customizable_list`. `customizable_init()` loads `selinux_customizable_types_path()` once.

Control flow: one-time initialization counts lines, rewinds, allocates a NULL-terminated list, strips trailing newline from each line, and stores duplicates. Lookup parses the context, extracts type, scans the list, and returns `1`, `0`, or `-1`.

State and persistence: `customizable_list` is process-global and never freed in this file. It persists after first use.

Dependencies and integration: uses context parser, path helpers, page size, and `__selinux_once`.

Risks and test signals: line counting includes blank/comment lines without filtering. Tests should cover missing file, invalid context, type match/no match, long lines bounded by page size, and allocation failure during list build.
