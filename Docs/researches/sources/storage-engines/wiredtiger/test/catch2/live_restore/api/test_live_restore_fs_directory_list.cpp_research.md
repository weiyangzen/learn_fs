# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fs_directory_list.cpp

## Purpose
Tests live-restore directory listing as a unified view over destination and source directories. It verifies deduplication, tombstone hiding, subdirectory handling, prefix filtering, and temporary-file filtering.

## Important APIs, Types, And Functions
`directory_list` wraps `WTI_LIVE_RESTORE_FS::iface.fs_directory_list` and `fs_directory_list_free`, returning a `std::set<std::string>`. `file_list_equals` removes standard WiredTiger metadata files before comparison. `directory_list_subfolder` and `directory_list_prefix` specialize the wrapper.

## Control Flow
Each Catch2 section creates a fresh `live_restore_test_env`, mutates files in source and/or destination, calls directory listing, and compares normalized sets. Scenarios cover destination-only files, source-only files, files in both, mixed backing locations, tombstones hiding source files, subfolder names, missing and existing subfolders, nested subdirectories, listing within a subdirectory, prefix filtering, and ignoring `.lr_tmp` temporary files.

## State And Persistence Behavior
The unified directory view is derived from physical files in `WT_LR_DEST` and `WT_LR_SOURCE`. Tombstones are stop files in the destination and suppress source entries without removing source data. Temporary live-restore files are filtered from results.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `<set>`, and WiredTiger file-name constants such as `WT_METAFILE`, `WT_METADATA_TURTLE`, and `WT_HS_FILE`. It integrates with both live-restore directory-list and free APIs.

## Risks And Edge Cases
Important risks include duplicate names when a file exists in both directories, stale source entries after destination tombstones, returning children instead of subdirectory names, incorrect ENOENT behavior for subfolders, and leaking `dirlist` allocations. Prefix tests include empty prefix, exact prefix, suffix-only mismatch, long prefix, and temporary-file names.

## Test Signals
Expected sets must match after metadata-file removal, and missing subfolder listing must return `ENOENT`. Any leaked temporary file, duplicate behavior issue, or tombstone visibility bug changes the result set.
