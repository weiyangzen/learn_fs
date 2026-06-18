<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util_test.go -->
# Research: sources/user-network-fs/gcsfuse/common/util_test.go

Purpose: tests shared common utilities for kernel feature gating, shutdown composition, and file helpers.

Important APIs/types/functions: `TestIsKLCacheEvictionUnSupported`, `TestJoinShutdownFunc`, `TestCloseFile`, `TestWriteFile`, and `TestReadFile`.

Control flow: kernel tests replace `kernelVersionToTest` per case and restore it. Shutdown tests run in parallel and assert joined errors contain each expected message. File tests create temp files, write/read content, and close them.

State and persistence: uses temporary files and a mutable package variable. The kernel-version mock is restored with `defer` to prevent cross-test contamination.

Dependencies: Go testing, testify, temp filesystem access, and the utility functions under test.

Risks: the kernel-version test is table-driven but only covers current unsupported ranges. File-helper tests do not check shorter overwrite truncation behavior or fatal close failure.

Test signals: `go test ./common`; failures indicate regression in feature-gate regexes, error joining, or file helper behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util_test.go -->
