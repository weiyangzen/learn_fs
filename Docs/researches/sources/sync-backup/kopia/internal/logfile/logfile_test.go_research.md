# sources/sync-backup/kopia/internal/logfile/logfile_test.go

Purpose: validates CLI logging flags, console formatting/color, file log formatting, rotation limits, size sweeping, and cache marker creation.

Important APIs/types/functions: `logfile.Attach`, `testenv.NewInProcRunner`, `testenv.NewCLITest`, `verifyFileLogFormat`, `verifyJSONLogFormat`, `getTotalDirSize`, and CLI commands such as `repo create`, `snap create`, and `snap ls`.

Control flow: `TestLoggingFlags` runs real in-process CLI commands with different logging flags and verifies stderr content, timestamps, colors, and JSON/content log files. Rotation tests force tiny segment sizes and max file counts. Total-size tests create a source tree, run commands, then repeatedly shrink log budgets and assert directory size decreases. Cache marker test verifies both log subdirectories contain cache markers.

State/persistence behavior: tests create real temporary repositories, source directories, and log directories. Log segments, `latest.log`, and cache marker files are inspected on disk.

Dependencies/integration: high-level integration coverage across CLI, logging setup, snapshot commands, cachedir, clock, and filesystem. Regexes encode expected log line formats for UTC and local timezone.

Risks/test signals: these tests are broader and slower than unit tests because they run CLI workflows. Format assertions can fail on intentional logging format changes. Size sweeping has tolerance checks rather than exact file lists.
