# sources/test-tools/fio/trim.c

Purpose: implements fio TRIM/DISCARD scheduling helpers when `FIO_HAVE_TRIM` is enabled. It selects pending trim extents, prepares an `io_u` for a discard operation, and decides probabilistically whether a completed write should later be trimmed.

Important APIs/functions: `get_next_trim(td, io_u)` pops the oldest `io_piece` from `td->trim_list`, fills offset/length/file, optionally removes it from verify history if `trim_zero` is disabled, opens and references the file, and configures `io_u` as `DDIR_TRIM`. `io_u_should_trim(td, io_u)` compares a random value from `td->trim_state` against `trim_percentage`.

Control flow: requeued `io_u`s with an existing file are accepted immediately. Empty trim lists return false. Otherwise the selected `io_piece` is either freed after removal from verify structures or marked `IP_F_TRIMMED` so later reads can verify zeroed data.

State/persistence: mutates `td->trim_list`, `td->trim_entries`, `td->io_hist_tree/list`, `td->io_hist_len`, `io_piece` flags, file references, and `io_u` transfer fields. No persistent files are written.

Dependencies/integration: depends on fio list/rbtree IO history, file open/reference helpers, `thread_options.trim_zero`, and verify paths that understand `IP_F_TRIMMED`/`IO_U_F_TRIMMED`.

Risks/test signals: list/tree accounting must stay consistent or verify queues corrupt. Error opening a file after removing the trim entry drops the operation. Tests should cover trim with and without `trim_zero`, requeue path, tree/list removal, and percentage boundaries.
