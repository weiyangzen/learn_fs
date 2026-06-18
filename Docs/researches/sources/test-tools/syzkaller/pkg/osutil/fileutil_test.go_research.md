# sources/test-tools/syzkaller/pkg/osutil/fileutil_test.go

Purpose: Tests process temp directory allocation and file-content grep utility behavior.

Important tests: `TestProcessTempDir` repeatedly pre-creates stale instance directories, writes fake stale pid files, then concurrently requests new process temp dirs and asserts uniqueness. `TestGrepFiles` builds nested `.c` and `.txt` files and checks that only `.c` files containing target bytes are returned.

Control flow and state: The temp-dir test relies on `ProcessTempDir` cleanup of pid files whose process no longer exists. It uses goroutines and a mutex-protected set to detect duplicate directories. The grep test uses `FillDirectory` and `GrepFiles`.

Dependencies and integration: Covers Unix `ProcessTempDir` behavior from `osutil_unix.go` and `GrepFiles` from `fileutil.go`.

Risks: Fake pid `999999999` assumes no such process exists. The test is concurrency-sensitive but repeated to catch races.

Test signals: Good coverage for lock-protected temp instance allocation and extension-filtered grep.
