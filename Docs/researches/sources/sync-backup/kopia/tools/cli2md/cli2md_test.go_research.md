<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md_test.go -->
# sources/sync-backup/kopia/tools/cli2md/cli2md_test.go

This file tests Markdown flag escaping. `TestEscapeFlags` runs table cases through `escapeFlags` and checks expected backtick-wrapped CLI flags in plain text.

The test directly protects generated documentation formatting for command-line flags, especially avoiding accidental Markdown list or emphasis interpretation. It depends on `testify/require`.

Risks not covered include full page generation, filesystem deletion/writes, command flattening, front matter, sorting, and advanced/common section partitioning. The test is narrow but useful for the most text-sensitive helper.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md_test.go -->
