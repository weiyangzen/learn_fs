## sources/sync-backup/syncthing/lib/osutil/traversessymlink.go

Purpose: detects whether a path traverses a symlink or hits a non-directory component where a directory is expected.

Important APIs: `TraversesSymlinkError`, `NotADirectoryError`, and `TraversesSymlink(filesystem, name)`.

Control flow and state: the function cleans/splits the path, walks components from root toward the target with `Lstat`, allows missing final or intermediate components, returns `TraversesSymlinkError` for symlink components, `NotADirectoryError` for non-directory intermediate components, and nil for safe paths.

Dependencies and integration points: used by model request/puller code to prevent reading or writing through symlinks outside the folder root.

Risks: correctness depends on `Lstat` not following symlinks and on path cleaning preserving security boundaries. Race conditions remain possible between check and later open unless callers also use safe filesystem primitives.

Test signals: `traversessymlink_test.go` covers symlink, non-directory, missing, and benchmark cases; request tests cover end-to-end symlink traversal rejection.
