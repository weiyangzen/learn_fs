# sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker.go

Purpose: tracks directories under a version archive that can be removed after old files are cleaned.

Important APIs and control flow: `emptyDirTracker` is a map of directory paths. `addDir` adds non-root directories. `addFile` removes the file's directory and all ancestors from the candidate map, because they contain retained content. `emptyDirs` returns candidates sorted deepest-first by reverse string comparison, so children are removed before parents. `deleteEmptyDirs` removes each candidate through the supplied filesystem and warns on failures.

State and persistence: in-memory candidate set; `deleteEmptyDirs` mutates the version filesystem by removing directories.

Dependencies and integration: used by `trashcan.Clean` after deleting old files.

Risks: reverse lexicographic sort is intended to approximate deepest-first and works for nested paths in tests, but path-depth sorting would be more explicit. Removal failures are logged and ignored. Test coverage models nested keep/remove directories.
