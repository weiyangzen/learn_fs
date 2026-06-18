# File Research: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.h

This header declares libedit file completion APIs.

Key declarations:
- `fn_complete()` and `fn_complete2()` perform completion with generator callbacks, attempted-completion callbacks, break characters, optional suffix function, query threshold, and optional readline-style result fields.
- `FN_QUOTE_MATCH` requests quote-aware matching/escaping.
- `fn_display_match_list()` prints matches in columns.
- `fn_tilde_expand()` expands `~` paths.
- `fn_filename_completion_function()` generates filename matches.
- `completion_matches()` provides readline-compatible match collection.

Integration:
- Included by `filecomplete.c`, tests, and code binding completion commands.
- Uses `EditLine *` from `histedit.h`/internal headers.
