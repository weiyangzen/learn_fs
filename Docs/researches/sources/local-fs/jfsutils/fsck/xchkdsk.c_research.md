# File Research: sources/local-fs/jfsutils/fsck/xchkdsk.c

## Purpose
Implements the `jfs_fsck` program entry point and top-level phase orchestration. It owns global fsck state, parses command-line options, opens and validates the target aggregate, coordinates journal replay, runs phases 0-9, performs approved repairs, emits summaries, flushes modified metadata, and exits with fsck-compatible status codes.

## Key Elements
Defines global process state used across fsck modules: superblock buffer `sb_ptr`, aggregate record `agg_recptr`, block-map record `bmap_recptr`, volume/program names, directory Unicode scratch buffers, device I/O handle, block sizes, log device path, lost+found Unicode names, and dynamic-storage error context.

`main()` initializes global records, allocates the very-large buffer, runs `initial_processing()`, starts the heartbeat, executes phases 0 through 9 unless early completion is requested, performs final processing and buffer flushes, records end time/return code in the fsck workspace control page, marks the aggregate clean or dirty, ends service logging, releases workspace, closes the volume, and returns `exit_value`.

`initial_processing()` starts the fsck service log, parses options, checks mount status, verifies parameters, opens the volume, validates/repairs the superblock, computes aggregate layout fields from the superblock, initializes alternating fsck service-log regions, and establishes valid fileset data block bounds. `parse_parms()` supports `-a`, `-p`, `-r`, `-f`, `-j`, `-n`, `-o`/`--omit_journal_replay`, `--replay_journal_only`, `-d`, `-v`, `-V`, and `-y`. `verify_parms()` resolves option interactions and selects message level.

The phase functions define the high-level checker pipeline:
- Phase 0 replays the journal unless omitted, handles clean-if-dirty/autocheck early exit, and releases logredo workspace.
- Phase 1 initializes I/O/workspace, records fixed metadata, selects and validates AIT, builds fileset workspace, validates metadata and fileset inodes, records block ownership, and detects fatal duplicate metadata allocations.
- Phase 2 checks directory integrity and link counts.
- Phase 3 resolves first references for duplicate blocks and validates parent relationships.
- Phase 4 reports inode problems and decides approved repairs.
- Phase 5 checks connectedness when write access is available.
- Phase 6 marks the filesystem dirty, resolves/creates `/lost+found`, allocates directory buffers, performs inode repairs, and reconnects orphaned inodes.
- Phase 7 rebuilds or verifies inode allocation maps/tables and replicates aggregate inode structures.
- Phase 8 rebuilds or verifies the aggregate block allocation map.
- Phase 9 reformats the journal if log replay failed and write access is available.

`check_parents_and_first_refs()` traverses fileset inode records, resolves duplicate-block first references, detects unallocated inodes referenced by directories, finds missing parent links, flags directory hard-link cases, and marks incorrect directory parent inode numbers for repair.

`report_problems_setup_repairs()` walks flagged inode records, displays paths, reports selected releases, corrupt data trees, duplicate claims, EA/ACL issues, inline EA flag fixes, bad directory entries, and directory index rebuilds. In read-write mode it approves implied repairs such as parent directory adjustment; in read-only mode it clears repair flags and marks the aggregate dirty where appropriate.

`repair_fs_inodes()` applies approved inode-level repairs: releases bad inodes, adjusts link counts, corrects directory parents, clears EA/ACL fields, toggles inline EA bits, rebuilds directory indexes, removes bad directory entries, and writes modified inodes.

`resolve_lost_and_found()` and `create_lost_and_found()` locate, validate, or create `/lost+found` for reconnect processing. They ensure the target is an in-use directory without unresolved dangerous duplicate claims, initialize a spare inode if needed, add the root directory entry, and set aggregate reconnect state.

`final_processing()` reports aggregate block discrepancies and usage summaries, updates external-log device information, replicates the superblock in read-write mode, and emits standard capacity/inode/directory/file/EA/ACL/free-space messages.

## Dependencies
Depends on most fsck subsystems: workspace allocation and block-map routines, inode validation/repair, directory checking and reconnect code, aggregate/fileset inode-map rebuild/verify code, block allocation map rebuild/verify code, superblock validation/replication, journal replay (`jfs_logredo`), journal formatting (`jfs_logform`), message/logging code, device open/close/mount helpers, Unicode helpers, and JFS on-disk structure macros.

## Behavior/Risks
The checker is global-state driven. Phase functions mainly coordinate subsystem calls and mutate `agg_recptr` flags such as `fsck_is_done`, `processing_readonly`, `processing_readwrite`, `corrections_needed`, `corrections_approved`, `ag_dirty`, and `ag_modified`.

Read-only mode is not just a file-open mode; it changes phase behavior, disables repair approval, may skip journal replay depending on options, and converts would-be fixes into dirty/error reporting.

The repair phase deliberately marks the superblock dirty before applying changes, then later final processing and `agg_clean_or_dirty()` decide whether the aggregate can be marked clean. Interrupted repair therefore leaves an intentionally unmountable/dirty filesystem.

Mount checking can ask the user to continue for mounted or non-JFS-mounted devices unless the selected mode allows read-only reporting. `-r` and `-y` are compatibility options rather than distinct interactive behavior.

There is a suspicious reserved-space calculation in `final_processing()` using `kbytes_total - -kbytes_for_dirs ...`, which should be reviewed before relying on the reported reserved-kilobyte summary.
