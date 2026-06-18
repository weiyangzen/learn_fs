# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/strings.c

Purpose: provides a small rbtree-backed string set used by pass 2 to detect duplicate directory entry names.

Read coverage: complete file read, 149 lines.

Key responsibilities:
- Stores variable-length strings in an rbtree ordered by length first and then byte comparison.
- Checks whether a string already exists without insertion.
- Inserts a string and optionally reports whether it was already present.
- Tracks approximate allocated bytes so pass 2 can bound memory use.
- Frees all string entries and resets allocation accounting.

Important entry points:
- `o2fsck_strings_init()`
- `o2fsck_strings_insert()`
- `o2fsck_strings_exists()`
- `o2fsck_strings_free()`
- `o2fsck_strings_bytes_allocated()`

Dependencies:
- Uses libocfs2/kernel rbtree types exposed through fsck headers and standard `malloc`/`free`.

Risk and edge cases:
- Ordering is not lexicographic by design; it only needs a stable equality-search ordering for duplicate detection.
- Stored strings are compared by explicit length and bytes. The comment says “null terminated,” but allocation/copying stores exactly the supplied bytes; current callers do not rely on a terminator for stored entries.
- `o2fsck_strings_init()` sets the root but does not explicitly zero `s_allocated`; callers should use freshly initialized storage or ensure the field is clear.
