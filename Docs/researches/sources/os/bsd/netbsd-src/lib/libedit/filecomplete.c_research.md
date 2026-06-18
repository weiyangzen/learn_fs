# File Research: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.c

This file implements libedit filename completion, tilde expansion, shell-style escaping, match collection, match display, and completion key wrappers.

Key functionality:
- `fn_tilde_expand()` expands `~` and `~user` using `getpwuid_r()`/`getpwnam_r()` when available.
- `fn_filename_completion_function()` iterates directory entries and returns matches for a prefix, preserving directory prefixes and supporting tilde-expanded directory paths.
- `completion_matches()` repeatedly calls a generator function, builds a match list, and computes the common prefix in `matches[0]`.
- `fn_display_match_list()` sorts and displays matches in columns.
- `fn_complete2()` is the main completion engine.
- `fn_complete()` is a compatibility wrapper that enables quote matching unless an attempted completion function is supplied.
- `_el_fn_complete()` and `_el_fn_sh_complete()` are bindable libedit command wrappers.

Escaping logic:
- `needs_escaping()` identifies shell-special wide characters.
- `needs_dquote_escaping()` restricts escaping inside double quotes to `"`, `\`, `` ` ``, and `$`.
- `unescape_string()` removes backslashes for matching.
- `escape_filename()` applies shell escaping according to current quote context and appends a space or `/` for single matches.
- `find_word_to_complete()` scans backward from the cursor to find the completion word, respecting escaped break characters and optional special prefixes.

Completion flow:
- Determine whether the previous command was also completion; repeated completion lists matches.
- Find and optionally unescape the current word.
- Call an attempted completion function if provided; otherwise call `completion_matches()` with the filename generator.
- Replace the current word with the common match prefix.
- For a single match, optionally append a suffix from `app_func()` and close quotes.
- For multiple matches on list request, prompt when above `query_items`, then display columns.
- Free all match strings and temporary buffers.

Risks and notes:
- `fn_filename_completion_function()` uses static directory/name state, so it is not reentrant or thread-safe.
- Escaping is shell-oriented and carefully quote-context dependent; tests cover many special characters.
- User confirmation for large match lists reads from `stdin` directly.
- Some allocation failure paths free top-level arrays but not necessarily already collected individual strings.
