# sources/sync-backup/rsync/generator.c

## Purpose

`generator.c` contains logic exclusive to rsync's generator process. It walks the received file lists, decides what must be created, deleted, copied locally, hard-linked, or transferred, emits itemized change records, sends checksum blocks to the sender for delta transfers, coordinates hard-link completion, schedules delete phases, and performs final directory timestamp and permission repair.

## Important APIs, Types, And Functions

The main exported functions are `generate_files()`, `check_for_finished_files()`, `atomic_create()`, `quick_check_ok()`, `unchanged_attrs()`, and `itemize()`. `maybe_ATTRS_REPORT` and `maybe_ATTRS_ACCURATE_TIME` are exported reporting flags used by hard-link and attribute paths.

Important internal routines include delete-delay helpers `start_delete_delay_temp()`, `flush_delete_delay()`, `remember_delete()`, `read_delay_line()`, `do_delayed_deletions()`, per-directory deletion `delete_in_dir()` and `do_delete_pass()`, metadata comparators `mtime_differs()`, `any_time_differs()`, `perms_differ()`, `ownership_differs()`, `acls_differ()`, and `xattrs_differ()`, block-signature generation `sum_sizes_sqroot()` and `generate_and_send_sums()`, alternate-basis selection `find_fuzzy()`, `try_dests_reg()`, `try_dests_non()`, local copy helper `copy_altdest_file()`, the main per-entry state machine `recv_generator()`, hard-link skip handling `handle_skipped_hlink()`, and directory finalization `touch_up_dirs()`.

## Control Flow

`generate_files()` sets itemizing/log behavior from protocol role and daemon/server status, computes flags for directory retouching, delete behavior, and delta mode, optionally runs a delete-before pass, then loops over `cur_flist` entries in sorted order. In incremental recursion, it first processes a parent directory pseudo-entry and can wait for more receiver file lists when hard-link lookahead is needed. Each active entry is converted to a path and passed to `recv_generator()`. After each entry it drains hard-link and redo completions via `check_for_finished_files()`, sends keepalives or socket flushes, advances through incremental file lists, and finally coordinates phases with `NDX_DONE` markers and `MSG_DONE` counts.

`recv_generator()` is the core decision engine. It starts with static cursors for parent directory tracking, dry-run missing subtrees, skipped subtrees, and fuzzy basis lists. It handles list-only output, daemon receive filters, dry-run parent absence, validation that parent dirs appear in non-incremental file lists, and `--delete-missing-args`. It implements `--ignore-non-existing`, `--ignore-existing`, destination type checks, permission-mode adjustment when not preserving perms, directory creation and later retouching, delete-during scans, symlink/device/special creation, regular-file size bounds, update-only logic, alternate-destination handling, partial-dir basis selection, fuzzy basis selection, backup creation, delta checksum emission, and success notifications for `--remove-source-files`.

For regular files, the generator first checks destination type and alternate basis directories. `quick_check_ok()` compares size and mtime, or checksum when `always_checksum` is enabled. `try_dests_reg()` searches `basis_dir[]` for increasingly strong matches: any regular file, quick-check match, and unchanged attributes. Depending on `--compare-dest`, `--copy-dest`, or `--link-dest`, it may report up-to-date, hard-link, local-copy, or return a basis file index. If delta transfer is needed, `generate_and_send_sums()` maps the basis file and writes weak and strong rolling checksum signatures.

Non-regular paths are handled inline. Directories are created or retouched and may trigger `delete_in_dir()`. Symlinks are checked for safety and created through `atomic_create()`. Devices and special files are created with `mknod` through `atomic_create()` when allowed. Unsupported non-regular files are skipped with informational output.

Deletion behavior is split by option. `delete_in_dir()` builds a local directory list with `get_dirlist()`, then deletes items absent from `cur_flist`, respecting mount points, `--one-file-system`, uid-write restrictions, daemon/local filters, and delayed deletion. `do_delete_pass()` runs that per directory for delete-before or delete-after. `--delete-delay` uses an in-memory buffer plus an unlinked temp file overflow; records are null-delimited mode/name entries optionally prefixed with `!` for uid-write restrictions.

`check_for_finished_files()` drains sender/receiver feedback. It handles hard-link completion indices, redo indices, old incremental file-list cleanup, directory touch-up for completed parent dirs, and `NDX_DONE` emission. `touch_up_dirs()` restores writable permissions and mtimes after contents are transferred.

## State And Persistence

Most state is in memory, but delete-delay may spill to an unlinked temporary file descriptor. Static variables inside `recv_generator()` persist across file entries and cache parent directory state, skipped subtree state, and fuzzy basis lists. Global `phase` tracks generator protocol phases. `deldelay_buf`, `deldelay_fd`, and counters hold delayed deletion data. `need_retouch_dir_times` and `need_retouch_dir_perms` persist whether a final directory pass is needed. File-list entries are mutated with flags such as `FLAG_MISSING_DIR`, `FLAG_DIR_CREATED`, `FLAG_FILE_SENT`, `FLAG_HLINK_DONE`, and hard-link predecessor fields.

## Dependencies And Integration Points

The generator consumes `cur_flist`, `first_flist`, `dir_flist`, `flist_eof`, and lookup helpers from `flist.c`; hard-link APIs from `hlink.c`; checksum and map-file APIs; transfer finalization and cleanup APIs; delete, backup, partial-dir, ACL, xattr, and filter modules; sender/receiver message APIs such as `write_ndx()`, `wait_for_receiver()`, `get_redo_num()`, and `get_hlink_num()`; and filesystem wrappers from rsync's portability layer. It emits checksum headers and itemize records to `sock_f_out`/`f_out`, which drive sender-side file data generation.

## Risks

`recv_generator()` is a dense state machine with many option interactions. Regressions can silently skip transfers, delete wrong files, or produce incorrect itemized output. Delete modes rely on `io_error` protection and must not run after unsafe file-list omissions. Alternate-destination paths can conflate real destination stat data with basis stat data if `stat_x` ownership is mishandled. Hard-link handling mutates linked-list fields and file-list progress counters, so skipped links and redo paths are fragile. In-place backups and copy-dest paths must preserve cleanup semantics to avoid leaving temp files or losing attributes. Delete-delay parsing is custom and must reject corrupt records. Directory retouching can fight permission constraints, fake-super behavior, and dry-run/list-only modes.

## Test Signals

Tests should cover quick-check by size, mtime, checksum, and nanoseconds; directory creation and final retouch; delete-before, delete-during, delete-delay, and delete-after; `--max-delete`; `--ignore-existing`, `--ignore-non-existing`, `--update`, min/max size; `--partial-dir`, fuzzy basis, compare/copy/link dest; symlink safety, device and special creation, write-devices; hard-link groups with skipped entries, delayed leaders, and incremental recursion; in-place backups; redo pass behavior; remove-source-files success messages; list-only output; ACL/xattr differences; one-file-system deletion; and protocol phase ordering with early delay/delete done messages.
