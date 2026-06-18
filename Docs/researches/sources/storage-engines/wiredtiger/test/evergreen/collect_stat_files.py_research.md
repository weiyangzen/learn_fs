<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/collect_stat_files.py -->
# sources/storage-engines/wiredtiger/test/evergreen/collect_stat_files.py

Purpose: gathers WiredTiger statistics log files from a build/test tree into a single directory for artifact packaging.

Important APIs: `collect_stat_files(destination_dir, source_dir, regex)` creates a unique destination subdirectory by stripping a leading `./` and replacing slashes with dashes, then copies all files in `source_dir` matching `WiredTigerStat.*`. `main()` walks the current tree, skips the destination directory, and calls the collector once for any directory containing a matching file.

State and persistence: creates destination subdirectories and copies stat files. It does not remove prior collected files.

Dependencies and integration: used in Evergreen upload-stat-files functions from `evergreen.yml` and `evergreen_disagg.yml`, usually from `wiredtiger/cmake_build`.

Risks and test signals: skip logic checks `if destination_dir in walk_dir`, which can skip unrelated paths containing the same substring. Destination naming can collide if different source paths normalize to the same dash-separated string. It only scans files directly in a directory, not recursively per collection call, but the outer `os.walk` covers recursion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/collect_stat_files.py -->
