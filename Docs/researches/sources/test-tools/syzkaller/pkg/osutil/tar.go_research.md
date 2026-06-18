# sources/test-tools/syzkaller/pkg/osutil/tar.go

Purpose: Archives a directory as tar or tar.gz, including directories and regular files while skipping other filesystem object types.

Important APIs: `TarGzDirectory` wraps `tarDirectory` with a gzip writer. `tarDirectory` writes tar headers and regular file contents.

Control flow: `TarGzDirectory` creates a gzip writer, defers close, and delegates to `tarDirectory`. `tarDirectory` walks the input directory, skips the root path, ignores non-directory/non-regular entries, computes slash-form relative paths, creates tar headers from file info, appends `/` to directory names, writes headers, and copies file data for regular files.

State and persistence: Reads filesystem contents and writes archive bytes to the supplied writer. It does not preserve symlink targets or special files.

Dependencies and integration: Used where syzkaller needs portable archive output, likely for artifacts or VM data transfer.

Risks: Walk order is filesystem-defined. Closing gzip/tar writers can surface errors only through deferred close timing; `TarGzDirectory` does not capture gzip close errors separately. Symlinks are skipped.

Test signals: `tar_test.go` verifies regular files in nested directories round-trip through raw tar generation.
