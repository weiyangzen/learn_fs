# sources/object-store/minio-mc/cmd/find_test.go

Purpose: Unit tests for `mc find` matching, path trimming, format substitution, and command exit status handling.

Important APIs/types/functions: `TestMatchFind`, `TestSuffixTrimmingAtMaxDepth`, `TestFindMatch`, `TestStringReplace`, and `TestGetExitStatus`.

Control flow: Tests create lightweight `findContext` values with S3 client stubs, verify ignore/name/path/regex/time/size matching, exercise max-depth truncation, validate wildcard name/path behavior, assert substitution tokens such as `{base}`, `{dir}`, `{size}`, and `{time}`, and check Linux exit statuses.

State and persistence: Spawns local commands in `TestGetExitStatus`; otherwise no persistence.

Dependencies/integration: Uses Go testing, regexp, exec, runtime guards, and time.

Risks: Linux-only exit-status test is skipped elsewhere. No tests for watch mode, metadata/tag regex maps, `{url}`, or `--exec` substitutions with shlex.

Test signals: Good coverage of the most error-prone pure functions in `find.go`.
