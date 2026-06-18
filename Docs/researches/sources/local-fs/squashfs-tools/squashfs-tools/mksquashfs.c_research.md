# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9091, source bytes 262135, report `Docs/researches/chunks/chunk_sources_local_fs_squashfs_tools_squashfs_tools_mksquashfs_c_1_1_9091_b669f446f92f_research.md`
- chunk 2: lines 9092-9227, source bytes 3892, report `Docs/researches/chunks/chunk_sources_local_fs_squashfs_tools_squashfs_tools_mksquashfs_c_2_9092_9227_e2e416a10caa_research.md`

## Chunk Research

### Chunk 1: lines 1-9091

# Chunk Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c lines 1-9091

## Scope

This chunk covers almost all of the `mksquashfs` implementation: global option and filesystem-build state, compression and metadata writers, file block/fragment deduplication, directory scanning and mutation passes, pseudo/action/exclude handling, append/recovery support, thread-pipeline setup, `sqfstar`, and most of `main()`.

The line boundary cuts through `main()` while setting up append mode after `read_filesystem()`. The final cleanup/writeout sequence is immediately after this chunk.

## APIs And State

- Global build options include compression toggles (`noI`, `noD`, `noF`, `noX`, `noId`), block size/log, fragment policy, duplicate checking, exportability, sparse detection, root/global mode/uid/gid overrides, timestamp reproducibility controls, tar/cpio/source style, hardlink and filesystem-boundary policy, xattr regex/add state, logging/info/progress controls, output offset/streaming mode, and append/recovery state.
- Filesystem assembly state is centralized in globals: `sBlk`, `total_bytes`, inode and directory metadata buffers/caches, fragment table, id table/hash, inode hash, duplicate block/fragment hash tables, inode numbering, source list, destination fd/path, output virtual/physical position, and old-root-entry lists used during append.
- Threading state is also global: caches/queues (`fragment_buffer`, `reserve_cache`, `fwriter_buffer`, `bwriter_buffer`, `to_reader`, `to_deflate`, `to_frag`, `to_order`, `to_writer`, `to_main`), pthread ids, and mutexes for fragments, lseek/fd position, duplicate lookup, and disk position.
- Public or cross-module functions visible in this chunk include `pre_exit_squashfs()`, `restorefs()`, `mangle()`, `read_bytes()`, `read_fs_bytes()`, `write_destination()`, `generic_write_table()`, `get_checksum_mem()`, `add_file()`, `write_file()`, inode lookup helpers, directory entry helpers, `do_directory_scans()`, `excluded()`, `open_info_file()`, `convert_to_action()`, and `main()`.
- On-disk format emission is done through Squashfs structs and swap macros from `squashfs_fs.h` / `squashfs_swap.h`: inode variants, directory headers/entries/indexes, fragment entries, id table, lookup table, xattr table, and superblock.

## Control Flow

- Startup:
  - `main()` records command lines via `SQFS_CMDLINE`, configures pager/help behavior, dispatches to `sqfstar()` when invoked under that name, finds source/output argument split, pre-scans for compressor selection and stdin-consuming modes, parses all options, validates conflicts, opens/creates/truncates or reads the destination, processes excludes and sort files, initializes threads, initializes the compressor stream, and sets initial output position.
  - `sqfstar()` is a tar-focused alternate entry path with mostly parallel option parsing. It forces tar mode, disables append, defaults exportability off and tail-end packing on, opens destination/stdout, processes exclude paths, initializes the same thread/compression/dedup infrastructure, then calls `process_tar_file()`.
- Compression and metadata:
  - `mangle2()` compresses a block with the selected compressor unless disabled, stores uncompressed data if compression is ineffective, and marks Squashfs compressed/uncompressed bits.
  - `get_inode()`, `write_inodes()`, `write_directories()`, and `write_dir()` buffer metadata in `SQUASHFS_METADATA_SIZE` chunks, compress them, write metadata-block length headers, and update uncompressed/compressed byte accounting.
  - `create_inode()` converts in-memory `dir_ent`/`inode_info` data into the correct Squashfs inode variant, choosing long inode forms when size, nlink, sparse, xattr, or directory-index state requires it.
  - `add_dir()` and `write_dir()` build packed directory records, create directory indexes when a metadata block boundary would be crossed, and decide short vs long directory inode form via `dir->dir_is_ldir`.
  - `generic_write_table()` writes arbitrary Squashfs metadata tables as compressed metadata blocks plus a swapped block-offset list; it is used by fragment, id, inode lookup, and xattr table writers.
- File-data path:
  - Reader threads from `reader.c` feed `to_deflate`; `deflator()` compresses file blocks or marks all-zero sparse blocks and posts ordered results to `to_main`.
  - `write_file()` consumes file buffers and delegates to empty, fragment-only, normal block, or duplicate-checking block paths.
  - `write_file_process()` handles streams where file size is initially unknown; it marks virtual position, accumulates block list/sparse accounting, and either creates a file record or rolls back on read error.
  - `write_file_blocks()` is the fast path when no possible duplicate is detected; `write_file_blocks_dup()` retains enough recent compressed buffers for byte comparison when a duplicate candidate exists.
  - `put_write_buffer_hash()` assigns virtual positions and sends compressed blocks through `to_order`; `orderer()` maps virtual positions to physical disk positions and hands buffers to `writer()`.
  - `frag_deflator()` compresses completed fragment blocks; `write_fragment()` queues them; `orderer()` records fragment table start/size before handing them to `writer()`.
- Deduplication:
  - `pre_duplicate()` cheaply checks block-list and fragment hash tables by first block size/count and fragment size.
  - `duplicate()` performs full duplicate resolution: block-list shape comparison, checksum over cached or on-disk compressed blocks, byte-by-byte comparison, fragment checksum/content comparison, partial duplicate composition, virtual-position rollback, and insertion or linking of `file_info` records.
  - `frag_duplicate()` handles fragment-only matches and can synthesize a fragment-only duplicate file from a larger file that shares the same tail fragment.
  - Append mode seeds duplicate tables with `add_file()` for files from the existing filesystem.
- Directory/source scanning:
  - `dir_scan1()` recursively builds the in-memory directory tree from real files, applying old inode-based excludes, wildcard/regex path excludes, one-filesystem policy, depth limits, and exclude actions during the scan.
  - `scan_single()`, `scan_encomp()`, `dir_scan()`, `process_source()`, and `no_sources()` create the root/dummy-root structure for single source, multiple source, tarstyle/cpiostyle source lists, or pseudo-only images.
  - `do_directory_scans()` orchestrates the post-scan passes: pseudo/action application (`dir_scan2()`), move actions (`dir_scan3()`), prune actions (`dir_scan4()`), empty-dir actions (`dir_scan5()`), deterministic directory sort and inode numbering (`dir_scan6()`), file-data writing (`dir_scan7()` or sort-driven writer), and metadata emission (`dir_scan8()`).
  - Symlink dereference actions are two-phase: `dir_scan_deref()` only marks symlinks, then `dir_deref()` mutates/deletes/clones directory subtrees to preserve action-test consistency.
  - `dir_scan8()` recursively creates non-directory inodes, recursively writes child directories, reuses already-created inodes for hardlinks/root entries, and appends each entry to the parent directory buffer.
- Append and recovery:
  - `read_super()` / `read_filesystem()` are used in `main()` to read an existing image, restore compressor/format options, load old metadata, old root entries, fragment table, inode lookup, and counters.
  - `write_recovery_data()` writes a recovery file containing an id string, original superblock, and original metadata tail; `read_recovery_data()` validates and restores it.
  - `restorefs()` restores saved metadata/xattr/counter state, rewrites filesystem tables and superblock, truncates/pads as needed, closes output, deletes the recovery file, and exits after abnormal append cancellation.

## Dependencies

- Local Squashfs modules: format definitions/swap macros, `mksquashfs.h`, compressor abstraction, xattrs, pseudo files, actions, progress/info/error helpers, caches/queues/lists, existing-filesystem reader, restore thread, fragment processor, tar reader, sort lists, merge sort macro, memory/alloc wrappers, thread readers, rate limit, virtual disk position map, uid/gid parsers, date/symbolic-mode helpers via included headers.
- POSIX and libc APIs: `open`, `read`, `write`, `lseek`, `close`, `ftruncate`, `stat`, `lstat`, `fstat`, `opendir/readdir/closedir`, `readlink`, `unlink`, `getcwd`, `getuid/getgid`, `getpwuid/getgrgid`, `pthread_*`, `signal`, `regex`, `fnmatch`, `strtoll`, environment variables, and block-device/regular-file checks.
- External behavioral dependencies include compressor plugins, xattr support availability, `/proc` or platform support for physical memory discovery, terminal pager settings, `SOURCE_DATE_EPOCH`, optional command-line logging via `SQFS_CMDLINE`, and tar parsing from `tar.c`.

## Notable Behavior

- Streaming mode writes a temporary streamed magic at the start and writes the final superblock at the end; it disables duplicate checking, progress, and summary output because stdout cannot be seeked or polluted.
- Normal output reserves the superblock area first, writes optional compressor options after it, writes data/metadata after that, then overwrites the real superblock at `SQUASHFS_START`.
- Reproducibility controls are strict: command-line timestamp controls, `SOURCE_DATE_EPOCH`, `-repro`, and `-repro-time` have explicit conflict checks.
- `-noI` implies id-table compression behavior for backward compatibility by resetting `noId` when both are set.
- Directory ordering is deterministic through linked-list merge sort before inode numbers and metadata are generated.
- Hardlink detection hashes non-directory `struct stat` records after clearing atime fields to avoid false negatives from access-time changes.
- Root entries from an appended filesystem are represented as `inode_info` objects with `root_entry = TRUE`; scan iterators skip or preserve them depending on pass.
- Old excludes use device/inode identity, while wildcard/regex excludes build a component trie with optional sticky `"... "` paths.
- Pseudo definitions can add files/directories/devices/symlinks, modify metadata, and attach pseudo xattrs. With `pseudo_override`, global uid/gid/mode overrides are delayed into the pseudo/action pass.
- Sparse block handling stores zero compressed size entries, but only reports sparse stat accounting when the original file appeared sparse.

## Risks

- This file relies on large mutable global state shared across many passes and worker threads; ordering mistakes can corrupt output state rather than being locally contained.
- `pathname()` and `subpathname()` return static buffers, so callers must not retain them across later calls or concurrent use. Most use is immediate, but this is fragile in threaded-adjacent code.
- `read_bytes()` and `write_bytes()` do pointer arithmetic on `void *`, a GNU C extension rather than portable ISO C.
- Deduplication reads back just-written data from writer caches or disk and depends on virtual-to-physical mapping correctness; rollback via marked virtual positions is subtle.
- Several fixed-size symlink buffers use 65536 bytes and reject exact-size returns, but mistakes around 65535/65536 limits would affect boundary symlinks.
- Appending must preserve old metadata and root-entry semantics while rewriting metadata tables; failures are mitigated by recovery files and `restorefs()`, but the state snapshot is complex.
- `check_sqfs_cmdline()` appends command lines to an environment-selected file after checking no symlink, no hardlink, and no execute bits, but this remains an externally controlled audit/log side effect.
- Many fatal paths call `BAD_ERROR()` / `EXIT_MKSQUASHFS()` from deep helper code, making error recovery coarse-grained.
- UID/GID offset is applied at the end to id table entries; late failure aborts after most image work has already been done.

## Cross-Chunk References

- Lines after 9091 finish `main()` append setup, dispatch to `process_tar_file()`, `process_source()`, `no_sources()`, or `dir_scan()`, fill the final superblock fields, flush pending fragment action buffers, sync/cancel the writer, apply uid/gid offset, write all filesystem tables, pad/truncate, write the superblock, close output, delete recovery file, print summary, close log, and return.
- `initial_reader`, `frag_thrd`, `process_tar_file`, `eval_*_actions`, `sort_files_and_write`, `generate_file_priorities`, `read_super`, `read_filesystem`, `restore_xattrs`, `save_xattrs`, `write_xattrs`, `read_xattrs`, `get_frag_action`, and virtual-position helpers are external to this file/chunk and are required to complete the pipeline.
- The final per-file report should merge this chunk with the short post-9091 tail rather than treating this chunk as a complete file-level report.

### Chunk 2: lines 9092-9227

# Chunk Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c lines 9092-9227

## Scope

This report covers `sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c` lines 9092-9227 for subset A (`Docs/research_subset_a.md`). The chunk is the final tail of `main()`: it finishes append-mode state preservation, reconfigures in-memory inode/directory caches for appending, dispatches the selected input scanner, fills the Squashfs superblock, drains pending fragment writes, serializes metadata tables, pads/truncates the destination, writes the final superblock, and closes/logs/prints summary state. It does not create or update the merged per-file report.

## Public And Internal APIs Covered

- `write_recovery_data(&sBlk)` records the original metadata tail for append recovery before any new filesystem content is committed.
- `save_xattrs()` snapshots append-time xattr state so abort/recovery can restore xattr accounting consistently with the earlier saved inode, directory, fragment, id, and count globals.
- `add_old_root_entry(root_name, sBlk.root_inode, inode_dir_inode_number, SQUASHFS_DIR_TYPE)` records the previous root directory as an entry when `-root-becomes` turns the old root into a subdirectory of the new root.
- Source dispatch calls exactly one of `process_tar_file(progress)`, `process_source(progress, deref, deref_keep)`, `no_sources(progress)`, or `dir_scan(S_ISDIR(source_buf.st_mode), progress, deref, deref_keep)`.
- `SQUASHFS_MKFLAGS(...)` packages compression/id/xattr/fragment/export/duplicate options into `sBlk.flags`.
- `get_frag_action(fragment)` and `write_fragment(*fragment)` flush fragment buffers left open by the file scan.
- `sync_writer_thread()` waits for writer completion; `pthread_cancel(writer_thread)` stops the writer after all queued data should be drained.
- `check_id_table_offset()` validates final id-table entries after `-uid-gid-offset`.
- `write_filesystem_tables(&sBlk)` writes inode, directory, fragment, optional lookup, id, and xattr tables and updates superblock offsets, `bytes_used`, compression id, and total-size accounting.
- `progressbar_finish()`, `ftruncate()`, alignment padding, `write_superblock(&sBlk)`, `close(fd)`, recovery-file unlink, `print_summary()`, and log close finish the command.

## Control Flow And Behavior

- The chunk begins inside append setup after the existing filesystem has already been read. It continues saving old counts and id/duplicate state, then writes recovery data and saves xattrs.
- With `root_name` set, the old root becomes a child directory in the new root. The code reserves two new inode numbers, moves the uncompressed directory tail to the front of `directory_data_cache`, injects an old-root entry, updates directory totals, and increments `dir_count`.
- Without `root_name`, appending targets the original root directly. The code saves the compressed directory region for rollback, rewinds directory bytes/cache bytes to the original root directory boundary, and reserves one new inode number.
- In both append cases, inode and directory cache sizes/positions are reset so new metadata appends from the old root/table boundary.
- `inode_count` is recomputed from object counters, then later copied into `sBlk.inodes`.
- The scan dispatcher chooses tar input, tar/cpio-style source, pseudo-only source, or normal directory scan. The returned inode becomes `sBlk.root_inode`.
- Superblock identity and options are finalized: magic, version, block size/log, flags, and mkfs time. Time precedence is explicit: command-line `mkfs_time`, latest inode time, then `time(NULL)`.
- Remaining fragment actions are flushed before writer synchronization and final table writing.
- Regular non-streaming outputs are truncated to `start_offset + get_dpos()`. Block devices and streaming outputs skip truncation.
- Unless `nopad` is set, the output is zero-padded to a 4096-byte boundary. The final superblock is written after padding.
- On success, any recovery file is removed, summary/log output is closed, and `main()` returns `0`.

## State And Data Structures

- `sBlk` is mutated from append input state into final output state: `root_inode`, `inodes`, magic/version, block layout, flags, and mkfs time are set here.
- Append rollback globals saved/configured here include `sdir_count`, `sfifo_count`, `ssock_count`, `sdup_files`, `sid_count`, `sdirectory_bytes`, `sdirectory_compressed_bytes`, and `sdirectory_compressed`.
- Active metadata-position globals adjusted here include `inode_bytes`, `inode_size`, `directory_size`, `cache_size`, `directory_cache_size`, `directory_bytes`, `directory_cache_bytes`, and `cache_bytes`.
- Inode numbering state is reset through `root_inode_number`, `inode_no`, and `inode_start_no`.
- Directory buffers are manipulated directly with `memmove()` and `memcpy()`.
- Fragment state flows through `fragment_table`, `fragments`, fragment actions, fragment mutex/queue state, and the writer queue.
- Output positioning depends on `fd`, `start_offset`, `get_dpos()`, `block_device`, `streaming`, and `nopad`.

## Dependencies

- This chunk depends on the preceding append-read setup from `read_filesystem()`, which populates old superblock state, inode/directory caches, table offsets, object counts, fragment tables, and root directory metadata.
- Recovery depends on earlier failure handling and `restorefs()`, which consumes the saved `s*` globals.
- Directory/source ingestion is implemented earlier by `process_tar_file()`, `process_source()`, `no_sources()`, and `dir_scan()`.
- `add_old_root_entry()` feeds append-aware directory handling such as `handle_root_entries()`.
- Metadata table writing delegates to `write_inodes()`, `write_directories()`, `write_fragment_table()`, `write_inode_lookup_table()`, `write_id_table()`, and `write_xattrs()`.
- Thread/queue correctness depends on previously initialized writer, fragment, orderer, and progress infrastructure.
- POSIX/C dependencies include `memmove()`, `memcpy()`, `time()`, `pthread_cancel()`, `ftruncate()`, `strerror()`, `close()`, and `unlink()`.

## Risks And Invariants

- Append mode must snapshot original state before mutation; mismatched saved counters/cache slices could make `restorefs()` write a malformed recovery image.
- The `root_name` and non-`root_name` append paths preserve different directory-table regions, so directory/cache boundaries must match the selected mode.
- In the root-becomes case, `sdirectory_compressed_bytes` is zero and no compressed-directory allocation is made; later zero-length restore copies must remain harmless.
- Inode-number offsets differ by append mode. Off-by-one errors could collide with old root entries or corrupt lookup/export tables.
- The fragment flush loop assumes `get_frag_action()` terminates and all queued fragments are handled before writer sync completes.
- Cancelling `writer_thread` after sync assumes no further queued data writes remain before synchronous metadata writes.
- `check_id_table_offset()` must run before emitting the id table so invalid offset-adjusted ids do not enter the image.
- Padding affects physical file length, not logical Squashfs `bytes_used`.
- The final superblock is written last, preserving append safety against interrupted builds.

## Cross-Chunk References

- The preceding chunk contains most of `main()` argument parsing, destination setup, compressor option emission, append filesystem reading, and the first half of original-state saving.
- Earlier same-file helpers used here include `write_fragment()` around line 1752, `dir_scan()` around line 3808, `process_source()` around line 5361, `no_sources()` around line 5479, `add_old_root_entry()` around line 5610, `write_recovery_data()` around line 6049, `write_filesystem_tables()` around line 6198, `write_superblock()` around line 6227, and `print_summary()` around line 6576.
- Top-of-file globals define append rollback buffers/counters, destination state, compression/options state, progress/logging flags, and helper prototypes.
- Separate xattr support supplies `save_xattrs()`, `restore_xattrs()`, and `write_xattrs()`.
- This is the final chunk of `mksquashfs.c`; all control-flow dependencies point backward to setup, scanning, queueing, metadata writing, and recovery helpers.
