# File Research: sources/os/bsd/netbsd-src/lib/libedit/emacs.c

This file implements emacs-style editing commands for libedit.

Key command functions:
- `em_delete_or_list()` handles `^D`: EOF at empty line, delete under cursor otherwise, and currently errors at end-of-line nonempty.
- `em_delete_next_word()` kills from cursor to the end of the next word.
- `em_yank()` inserts the kill buffer.
- `em_kill_line()` kills the whole line.
- `em_kill_region()` and `em_copy_region()` operate on the mark/cursor region.
- `em_gosmacs_transpose()` and `em_delete_prev_char()` implement emacs variants of transpose/backspace.
- `em_next_word()`, `em_upper_case()`, `em_capitol_case()`, and `em_lower_case()` perform word movement/case changes.
- `em_set_mark()` and `em_exchange_mark()` manage the mark.
- `em_universal_argument()` multiplies the argument by 4.
- `em_meta_next()` marks the next input as meta.
- `em_toggle_overwrite()` toggles insert/overwrite mode.
- `em_copy_prev_word()` copies the previous word at the cursor.
- `em_inc_search_next()` and `em_inc_search_prev()` start incremental history search.

Important control flow:
- Most text manipulation uses shared helpers from `chared.c`.
- Word operations use emacs word classification `ce__isword`.
- Kill/yank operations manipulate `el_chared.c_kill`.
- Some commands are vi-aware when called in vi maps, completing operator-pending actions.

Risks and notes:
- `em_yank()` rejects insertion when the kill buffer would exceed the current line limit rather than attempting buffer growth.
- Mark-based commands require `c_kill.mark` to be set.
- The function name `em_capitol_case()` preserves historical spelling.
