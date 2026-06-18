# sources/sync-backup/borg/src/borg/archiver/compact_cmd.py

## Purpose

`compact_cmd.py` implements `borg compact`, Borg's repository garbage collection command. It scans repository objects, determines which objects are still referenced by live archives, deletes unused objects, cleans soft-deleted archive entries, refreshes the repository chunk index, and removes files-cache entries for archive series that no longer exist. The source was read as a complete 277-line file.

## Important APIs, Types, and Functions

`ArchiveGarbageCollector` owns compaction state: `repository`, `manifest`, `chunks`, `total_files`, `total_size`, `archives_count`, `stats`, and `iec`. `garbage_collect()` orchestrates the operation. `get_repository_chunks()` builds the object index either from `repo_lister()` with stored sizes for `--stats` or from `build_chunkindex_from_repo()` for the fast path. `analyze_archives()` walks all archive metadata and item chunks, marking referenced object IDs. `report_and_delete()` reports missing objects, purges soft-deleted archive entries via `manifest.archives.nuke_by_id()`, deletes unused repository objects, and logs statistics. `save_chunk_index()` writes the new full chunk index with `write_chunkindex_to_repo_cache()`. `cleanup_files_cache()` removes cache files whose generated archive-series suffix no longer maps to an existing series. `CompactMixIn.do_compact()` is the CLI entry point, and `build_parser_compact()` wires `--dry-run` and `--stats`.

## Control Flow

`do_compact()` opens the repository exclusively with delete compatibility and skips mutation when `--dry-run` is set. Normal compaction calls `garbage_collect()`, which first builds a chunk index for all objects, then analyzes every archive in timestamp order. For each archive it marks the archive metadata object, item pointer objects, item stream objects, and all content chunk IDs as used. It then reports missing referenced objects, removes soft-deleted archive directory entries, computes the unused ID set from unmarked chunk-index entries, deletes stale central chunk-index caches before any object deletion, deletes each unused repository object, writes a clean replacement chunk index, and cleans files-cache files.

## State and Persistence Behavior

The command mutates repository object storage by deleting unused objects and mutates the archives directory by permanently nuking soft-deleted archives. It persists an updated chunk index into the repository cache and deletes older chunk-index caches to avoid stale indexes after interrupted deletion. It also mutates the local cache directory under `get_cache_dir()/repository.id_str` by unlinking unused files-cache files. Missing referenced objects set Borg's global exit code to `EXIT_ERROR` but do not stop the deletion pass by themselves.

## Dependencies and Integration Points

This command integrates with `Archive` for archive metadata and item iteration, `Manifest` for archive listings and soft-deleted archive removal, `Repository`/`repo_lister()` for object enumeration and deletion, `ChunkIndex` for used/unused tracking, cache helpers for chunk-index and files-cache maintenance, and `ProgressIndicatorPercent` for progress output. It is coupled to the soft-delete lifecycle started by `delete_cmd.py` and `prune_cmd.py`, and to `repo_space_cmd.py` because compaction is the operation that actually frees storage after deletions.

## Risks and Edge Cases

The fast path trusts the cached chunk index enough to find repository object IDs; a stale or incomplete cache can make missing chunks appear. `--stats` is slower but builds from repository listings and knows object sizes. Interruptions during deletion are handled conservatively by deleting central chunk-index caches before object deletion, but an interrupted run still leaves partially compacted storage until the next rebuild. Files-cache cleanup assumes normal automatically generated cache suffixes and may not perfectly handle manually varied `BORG_FILES_CACHE_SUFFIX` values. Missing archive metadata or repository corruption can produce missing-object errors while compaction continues.

## Test Signals

Useful tests include compacting a repository after `delete`/`prune` and verifying unused objects disappear only after `compact`; comparing `--stats` and non-`--stats` behavior; interrupting deletion after chunk-index cache invalidation and verifying later create/check rebuilds safely; repositories with soft-deleted archives whose archive objects are already absent; missing referenced chunk fixtures that set an error exit; and files-cache directories containing both used and unused generated cache files.
