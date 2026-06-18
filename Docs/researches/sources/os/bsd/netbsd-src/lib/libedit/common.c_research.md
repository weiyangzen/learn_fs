# File Research: sources/os/bsd/netbsd-src/lib/libedit/common.c

This file implements editor-neutral libedit command functions shared by emacs and vi bindings.

Key command functions:
- Input and line completion: `ed_insert()`, `ed_newline()`, `ed_end_of_file()`, `ed_quoted_insert()`.
- Deletion: `ed_delete_prev_word()`, `ed_delete_next_char()`, `ed_kill_line()`, `ed_delete_prev_char()`.
- Movement: `ed_move_to_end()`, `ed_move_to_beg()`, `ed_next_char()`, `ed_prev_char()`, `ed_prev_word()`, `ed_prev_line()`, `ed_next_line()`.
- Arguments and ignored input: `ed_digit()`, `ed_argument_digit()`, `ed_unassigned()`, `ed_ignore()`, `ed_sequence_lead_in()`.
- Display: `ed_clear_screen()`, `ed_redisplay()`, `ed_start_over()`.
- History navigation/search: `ed_prev_history()`, `ed_next_history()`, `ed_search_prev_history()`, `ed_search_next_history()`.
- Extended command execution: `ed_command()`.

Important control flow:
- Insert mode honors `MODE_INSERT`, `MODE_REPLACE`, and `MODE_REPLACE_1`, using `c_insert()` and `re_fastaddc()`/`re_refresh()`.
- Vi operator-pending actions are completed by motion commands through `cv_delfini()`.
- History navigation saves the current line when leaving event 0, updates `eventno`, and uses `hist_get()` to load target history entries.
- History search uses `c_setpat()` and `c_hmatch()` from search helpers.
- `ed_command()` prompts with `"\n: "`, parses the resulting command with `parse_line()`, resets to key map, and refreshes.

Risks and notes:
- Many functions interpret `el_state.argument`; very large numeric arguments are capped indirectly in digit handlers.
- Behavior diverges for vi vs emacs maps, especially cursor bounds and EOF handling.
- Extended commands depend on generated command tables and parser integration.
