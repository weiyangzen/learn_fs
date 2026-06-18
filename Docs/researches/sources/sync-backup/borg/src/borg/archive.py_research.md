# sources/sync-backup/borg/src/borg/archive.py

## Purpose
`archive.py` is Borg's central archive model and archive data-plane implementation. It handles archive metadata, item-stream chunking, statistics, extraction, filesystem and tar object processing, chunk reuse, repository consistency checking and repair, and archive recreation. It bridges high-level CLI commands with repository objects, manifests, caches, cryptographic keys, chunkers, item metadata, platform metadata, and filesystem I/O.

## Important APIs, Types, and Functions
- `Statistics` tracks original size, deduplicated/unique size, file counts, status counts, chunking/hashing time, and remote byte counters, with text/JSON progress output.
- `BackupIO`, `backup_io_iter`, `OsOpen`, and `stat_update_check` wrap filesystem I/O errors into Borg backup exceptions and guard against file-type/inode race conditions between stat and open/fstat.
- `DownloadPipeline` fetches repository objects, parses them with `RepoObj`, replaces missing file chunks with zero bytes when requested, and unpacks item metadata streams.
- `ChunkBuffer` and `CacheChunkBuffer` pack `Item` dictionaries into msgpack streams, content-chunk the metadata stream, and write archive stream chunks through the cache.
- `archive_get_items` and `archive_put_items` abstract legacy v1 `items` lists versus v2+ `item_ptrs` indirection chunks.
- `Archive` loads, creates, saves, extracts, renames, deletes, and compares archives. It owns archive metadata, item iteration, `ArchiveItem` packing, manifest archive directory updates, and extraction attribute restoration.
- `MetadataCollector` reads mode, timestamps, ownership, names, inode, birthtime, BSD flags, xattrs, and ACLs according to backup options.
- `ChunksProcessor`, `cached_hash`, and `zero_chunk_ids` hash chunks, optimize all-zero chunk hashing, write chunks to the cache, and update file item chunk lists.
- `FilesystemObjectProcessors` builds `Item` records from live filesystem objects, handles hardlink tracking, special file treatment, files-cache reuse, chunkification, race detection for files changed while reading, and status accounting.
- `TarfileObjectProcessors` imports tar members into Borg items, including Borg-specific pax metadata, SCHILY xattrs/ACLs, hardlink chunk reuse, and file content chunking.
- `RobustUnpacker` and `valid_msgpacked_dict` support resynchronization while reading damaged item metadata streams during archive checks.
- `ArchiveChecker` performs archive consistency checks, optional cryptographic data verification, missing/corrupt manifest recovery, lost archive directory reconstruction, archive item stream validation, and repair writes.
- `ArchiveRecreater` recreates archives with filters, optional rechunking/recompression coordination, exclude-tag handling, metadata preservation, and original archive deletion.

## Control Flow
Archive creation starts with an `Archive(..., create=True)` and a `CacheChunkBuffer`. Filesystem or tar processors create `Item` objects, collect metadata, chunk file data, update stats, and call `Archive.add_item()`. `Archive.save()` flushes the item stream, writes `item_ptrs`, packs archive metadata as an `ArchiveItem`, adds the archive metadata chunk, waits for async repository responses, creates a manifest archive entry, and writes the manifest.

Archive reading loads metadata by archive name or id through the manifest, fetches the archive metadata object, parses/decrypts it, resolves item stream chunk ids, and iterates items via `DownloadPipeline.unpack_many()`. Extraction dispatches by item mode: regular files stream chunks to stdout/dry-run or to disk, directories are created/preserved, symlinks/fifos/devices are recreated, hardlinks are coordinated by `HardLinkManager`, and attributes are restored late to preserve ownership, xattrs/ACLs, timestamps, and flags.

Filesystem backup processing is race-aware. It stats by name, opens by directory fd/name where possible, fstats, checks type and inode stability, collects simple and extended metadata, excludes tagged items by xattr/flag, reuses files-cache chunks when valid, chunks changed content, checks whether ctime/mtime changed while reading, and memorizes unchanged files only when safe. Tar import follows a similar item creation path but derives metadata from `tarinfo` and pax headers rather than live filesystem calls.

Archive checking first builds a repository chunk index, obtains a key from the manifest or sampled chunks, optionally verifies all encrypted objects by parsing/decompressing them, loads or rebuilds the manifest, optionally scans all objects for lost archive metadata, and then validates selected archives. During archive validation it detects missing metadata/file chunks, validates msgpack item dictionaries against required/known keys, can resynchronize damaged streams, and in repair mode rewrites item pointer streams/archive metadata and manifest entries. `finish()` writes repaired manifest state and invalidates chunk-index caches.

Archive recreation opens a source archive, creates a target temporary/archive object, optionally adds tagged-directory excludes, filters items, reuses chunks or rechunkifies content, saves target metadata with original command/timestamp metadata as appropriate, and deletes the original archive when configured.

## State and Persistence Behavior
This module performs substantial persistent mutation: repository object writes via cache/repo objects, manifest writes, archive directory creates/deletes, chunk-index cache deletion, filesystem extraction writes, metadata restoration, and optional repository object deletion during repair. It also maintains in-memory state including archive stats, item buffers, hardlink maps, seen chunks, `zero_chunk_ids` LRU cache, progress state, and check error flags. Dry-run paths avoid writes for extraction/recreation/check repair, but many normal operations mutate repository or filesystem state.

## Dependencies and Integration Points
It depends on Borg subsystems for chunking, cache, crypto keys, constants, helpers, hash index, manifest, patterns, item types, platform ACL/xattr/flags, repository, and repo object formatting. It integrates with command mixins such as create/extract/list/info/diff/check/recreate/tar/import/export, with `_common.with_repository` for repository/cache lifecycle, and with shell/user output via loggers and progress indicators. Platform integration is extensive: POSIX ownership/mode/timestamps, Windows timestamp behavior, macOS dataless/nodump flags, BSD birthtime/flags, Linux xattrs/capabilities, and hardlink support.

## Risks and Edge Cases
- Race handling is security-critical. Any gap around `stat_update_check`, symlink handling, or fd-based access can lead to backing up the wrong object from a live filesystem.
- `ArchiveChecker --repair` is intentionally lossy in some corruption cases; it may delete corrupt chunks or remove broken archive entries.
- Missing chunks may be replaced with zeros during extraction/fetch paths, which preserves stream length but can hide data loss unless surfaced by logs/checks.
- Attribute restoration order is delicate; ownership can remove Linux capabilities, immutable flags must be set late, and platform support for symlink timestamps/permissions varies.
- Files-cache reuse depends on accurate metadata; incorrect changed-while-reading detection could archive inconsistent file content.
- `Archive.delete()` only removes manifest/archive-directory references and can orphan chunks until compaction.
- Robust msgpack resynchronization is heuristic and must balance recovery with avoiding false item interpretation.

## Test Signals
High-value tests include archive create/extract/list/info round trips, hardlink/symlink/fifo/device handling, ACL/xattr/bsdflags restoration, sparse extraction, files-cache reuse and invalidation, changed-while-reading retries, tar import/export with pax metadata, missing chunk behavior, archive compare output, recreate filtering/rechunking, and check/repair flows on deliberately damaged repositories. Platform CI is important because much behavior is OS-specific. Repository mutation tests should verify manifest/archive directory updates, chunk reference behavior, and cache invalidation after repair.
