# sources/test-tools/syzkaller/pkg/osutil/tar_test.go

Purpose: Tests tar archive creation for regular files.

Important test: `TestTarDirectory` creates three files, including nested and empty files, calls uncompressed `tarDirectory`, reads the tar stream back, and asserts the found regular-file contents equal the original map.

Control flow and state: Uses `FillDirectory` for setup, `bytes.Buffer` as archive sink, and `archive/tar.Reader` for verification.

Dependencies and integration: Directly covers `tarDirectory`, while `TarGzDirectory` is indirectly trusted because it only wraps gzip around the tar writer.

Risks: Does not verify directory headers, permissions, mtimes, gzip wrapper, symlink skipping, or deterministic order.

Test signals: Basic correctness guard for archive content.
