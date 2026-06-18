<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter.go

This file wraps fswalker reporter creation and comparison. `Report` writes a temporary report config, loads a reporter from it, and compares two in-memory walk protobufs. `ReportFiles` does the same for serialized walk files. `writeTempConfigFile` writes config textproto through `protofile`.

Control flow is temp-file based because upstream fswalker APIs consume config files. Cleanup uses `defer os.RemoveAll` on temp config paths.

State is transient config files and loaded report structures. Dependencies are `github.com/google/fswalker`, fswalker protobufs, and `protofile`. Risks include temp cleanup errors ignored, config file mode/contents, and upstream reporter behavior changes. Unit tests cover file-based reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter.go -->
