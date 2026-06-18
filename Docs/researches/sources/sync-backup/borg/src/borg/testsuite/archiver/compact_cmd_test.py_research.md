# sources/sync-backup/borg/src/borg/testsuite/archiver/compact_cmd_test.py

Purpose: tests `borg compact` output, behavior after archive deletions, chunk-index safety after interrupted compaction, and files-cache cleanup for deleted archives.

Important APIs/types/functions: tests use `cmd`, `create_src_archive`, `create_regular_file`, `open_repository`, `Manifest`, `ArchiveGarbageCollector`, cache helpers `get_cache_dir`, `files_cache_name`, `discover_files_cache_names`, and `list_chunkindex_hashes`.

Control flow: initial tests create empty or populated repositories, delete zero/some/all archives, run compact with and without `--stats`, and assert expected status/stat lines. `test_compact_index_corruption` repeatedly compacts to guard against incomplete index warnings. `test_compact_interrupted_does_not_poison_chunk_index` deletes the only archive containing unique content, instantiates `ArchiveGarbageCollector`, monkeypatches `save_chunk_index` to raise after object deletion, and asserts cached chunk indexes no longer list deleted objects; a subsequent identical backup must re-upload and extract correctly. `test_compact_files_cache_cleanup` records per-archive files cache names, deletes one archive, compacts, and verifies only remaining archive cache files exist.

State and persistence behavior: repository object stores shrink during compact, cache/chunk index files are invalidated or rewritten, files cache entries are removed, and archive manifests change after delete. The interruption test intentionally leaves a mid-compaction state.

Dependencies and integration points: covers compaction command, garbage collector internals, cache directory layout, chunk index discovery, manifest delete operation, extraction integrity after compaction, and local/remote/binary parametrization where applicable.

Risks: tests introspect cache files and GC internals, so implementation refactors can require test updates. The interruption scenario is critical because stale chunk indexes could cause future archives with dangling references.

Test signals: validates both user-facing compact output and a severe data-loss regression path involving interrupted deletion before chunk-index save.
