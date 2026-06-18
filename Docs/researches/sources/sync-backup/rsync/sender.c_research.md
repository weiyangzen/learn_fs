# sources/sync-backup/rsync/sender.c

Purpose: Sender-side transfer engine. It receives checksum sets from the generator, opens source files securely, maps file data, computes deltas, sends matched/literal data to the receiver, logs progress, and optionally removes source files after successful transfer.

Important APIs, types, and functions: Exports `extra_flist_sending_enabled`, `successful_send()`, and `send_files()`. Internal helpers are `receive_sums()` and `write_ndx_and_attrs()`.

Control flow: `send_files()` loops over indexes from `read_ndx_and_attrs()`, sends extra flists during incremental recursion, handles `NDX_DONE` phases, resolves file paths, logs non-transfer items, toggles redo/checksum/append/backup state based on `FLAG_FILE_SENT`, reads receiver checksums via `receive_sums()`, opens the source path using `secure_relative_open()` in secure daemon mode or `do_open_checklinks()` otherwise, maps the file, writes index/attrs and checksum header, runs `match_sums()`, emits progress/logging, unmaps/closes, frees sums, and marks the file sent. `successful_send()` re-stats and removes source files only if unchanged and not the destination in a local-server transfer.

State and persistence behavior: Mutates `file->flags`, stats counters, `io_error`, `make_backups`, `append_mode`, `csum_length`, `updating_basis_file`, and `extra_flist_sending_enabled`. It may delete source files when `--remove-source-files` is active.

Dependencies and integration points: Integrates with generator requests, receiver protocol, file-list APIs, checksum/match code, secure path resolver, xattr request exchange, batch mode, compression selection, progress, and logging.

Risks and test signals: Risks include secure daemon TOCTOU path handling, source deletion safety, append diminished-file behavior, device reads, batch output routing, phase synchronization, and redo state toggles. Tests should cover daemon secure symlink races, remove-source-files unchanged checks, append/inplace, device copy policy, batch mode, incremental recursion, and vanished files.
