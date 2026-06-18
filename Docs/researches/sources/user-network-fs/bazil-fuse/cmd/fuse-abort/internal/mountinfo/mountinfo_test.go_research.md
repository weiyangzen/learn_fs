<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo_test.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo_test.go

Purpose: regression tests for the mountinfo reader/parser.

Important APIs, types, and functions: covers `Open`, `Reader.Next`, `Reader.Close`, EOF handling, escaped fields, and malformed fuzzer crashers.

Control flow: `TestOpenError` checks not-exist behavior. `TestReal` scans a corpus file until a known FUSE mount is found and verifies major/minor/fstype. `TestEscape` validates octal unescaping. `TestCrashers` iterates a crasher corpus and ignores parse errors as long as there is no panic.

State and persistence behavior: reads static corpus files only.

Dependencies and integration points: depends on `testdata/fuzz/corpus` and the public mountinfo API.

Risks and test signals: coverage is limited to corpus examples, but fuzz crashers guard parser robustness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo_test.go -->
