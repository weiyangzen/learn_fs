# sources/sync-backup/rsync/rsync.c

Purpose: Shared rsync runtime routines used by multiple processes: charset setup/conversion, protected-arg transfer, index/attribute reading, file attribute application, signal handling, transfer finalization, file-list lookup, and role naming.

Important APIs, types, and functions: Exports `setup_iconv()`, `iconvbufs()`, `send_protected_args()`, `read_ndx_and_attrs()`, `free_sums()`, `dest_mode()`, `set_file_attrs()`, `sig_int()`, `finish_transfer()`, `flist_for_ndx()`, and `who_am_i()`. Internal `same_mtime()` compares file-list and stat mtimes with optional nanosecond accuracy.

Control flow: `setup_iconv()` initializes message checking and optional send/receive converters. `iconvbufs()` converts xbufs with support for expansion, circular output, and inclusion of bad/incomplete bytes. `read_ndx_and_attrs()` reads protocol indexes, handles incremental-recursion flist markers and delete stats, updates `cur_flist`, reads item flags/basis types/xnames, and validates transfer requests. `set_file_attrs()` stat/xattr/ACL-loads as needed, computes ownership/group/time/create-time/mode changes, applies them, and reports itemized names. `finish_transfer()` handles backups, pre-rename attrs, robust rename/copy fallback, and final attrs.

State and persistence behavior: Mutates global iconv descriptors, `cur_flist`, stats-related state indirectly, file flags such as `FLAG_TIME_FAILED`, and filesystem metadata. `sig_int()` sets `got_kill_signal` for controlled shutdown or exits.

Dependencies and integration points: Central integration point for rsync protocol, file-list management, logging, ACL/xattr modules, backup/rename helpers, charset libraries, and process-role globals.

Risks and test signals: Risks include protocol desynchronization in `read_ndx_and_attrs()`, metadata privilege edge cases, symlink time/chown portability, iconv buffer wrap errors, and robust rename fallback with partial dirs. Tests should cover protocol versions, incremental recursion, ACL/xattr preservation, fake-super, symlink metadata, iconv protected args, and signal cleanup.
