# sources/sync-backup/rsync/receiver.c

Purpose: Receiver-side transfer engine. It opens basis/output files, receives delta tokens, reconstructs destination files, validates whole-file checksums, handles partial/delayed/inplace updates, and coordinates redo/success messages.

Important APIs, types, and functions: Exports `get_tmpname()`, `open_tmpfile()`, and `recv_files()`. Key internal helpers are `secure_basis_open()`, `receive_data()`, `discard_receive_data()`, `handle_delayed_updates()`, `no_batched_update()`, `we_want_redo()`, and `gen_wants_ndx()`.

Control flow: `recv_files()` loops over file indexes and item flags from `read_ndx_and_attrs()`, handles non-transfer item logging/xattrs, rejects transfer requests in phase 2, toggles checksum/append/backup settings for redo phase, selects a basis file based on protocol and `fnamecmp_type`, opens an output path either inplace or temporary, calls `receive_data()`, closes fds, finalizes with `finish_transfer()` or partial-dir retention, and sends success/redo/no-send messages. `receive_data()` reads the checksum header, maps the basis file, processes literal and matched-block tokens, writes data or skips matched inplace ranges, updates transfer checksums, handles sparse/preallocated/truncated files, fsyncs if requested, and compares against the sender checksum.

State and persistence behavior: Static `phase`, `redoing`, `batch_redo_list`, `delayed_bits`, and `updating_basis_or_equiv` drive multi-phase and redo behavior. Persistent filesystem effects include temp files, partial-dir files, delayed-update renames, backups, chmod/chown/mtime/xattr updates via `finish_transfer()`, and optional source-removal success messages.

Dependencies and integration points: Deeply integrated with rsync protocol, file lists, generator pipe, checksum/mapping/token code, logging, filters, xattrs, ACLs through shared helpers, secure path functions, and global options from `options.c`/main state.

Risks and test signals: High-risk areas are symlink race hardening, absolute partial/backup basis handling, no-basis match tokens, sparse/inplace truncation, redo checksum length toggles, delayed update atomicity, daemon filters, and batch mode ordering. Tests should include partial-dir absolute paths, non-chroot daemon secure symlink races, inplace redo, append/append-verify, sparse files, vanished/basis-dir cases, and checksum verification failures.
