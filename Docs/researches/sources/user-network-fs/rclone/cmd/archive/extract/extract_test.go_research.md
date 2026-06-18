# sources/user-network-fs/rclone/cmd/archive/extract/extract_test.go

Purpose: unit test for the path normalization rule used by archive extraction. `TestStripDotSlashPrefix` verifies that `strings.TrimPrefix(input, "./")` strips a single leading `./`, leaves normal paths unchanged, preserves `../` traversal-looking paths, converts `./` to empty, and strips only once.

State is none beyond table-driven assertions. Dependencies are `testing`, `strings`, and testify assert. This is a focused regression test for the extraction behavior that avoids creating a spurious encoded `.` directory from common tar entries. Risk not solved by the test: it explicitly confirms `../` is not stripped, so path traversal prevention must come from other layers or remains a concern. Additional integration coverage comes from archive round-trip tests.
