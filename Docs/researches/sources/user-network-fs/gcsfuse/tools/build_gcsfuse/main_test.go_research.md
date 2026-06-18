<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main_test.go

Purpose: Integration-style Go test that verifies `buildBinaries` stamps the requested version into the built gcsfuse binary.

Important APIs, types, and functions: `TestVersion` creates a temp destination, calls `buildBinaries(dir, "../../", "99.88.77", runtime.GOARCH, nil)`, and runs the produced `bin/gcsfuse` with `--version` and `-v`, asserting output contains `gcsfuse version 99.88.77`.

Control flow: Temp dir is cleaned with `t.Cleanup`. Build failures fail the test immediately. Each version flag case runs as a subtest with `exec.Command(...).CombinedOutput`.

State and persistence behavior: Writes build outputs only under a temporary directory and deletes them after test. It compiles the local source tree and executes the resulting binary.

Dependencies and integration points: Depends on a working Go toolchain, repository-relative source path `../../`, host architecture, and `testify/assert`.

Risks and test signals: This is a high-signal test for release version injection but is slower and more environment-sensitive than a unit test. It does not inspect mount helper outputs or cross-architecture behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/build_gcsfuse/main_test.go -->
