## sources/sync-backup/restic/internal/global/global_test.go

Purpose: unit tests for repository location reading, empty-password handling, and environment override precedence for global options.

Important tests: `TestReadRepo` covers direct repo path, repository-file reading with trimming, and missing repository-file errors. `TestReadEmptyPassword` validates `InsecureNoPassword` and conflict with supplied password. `TestPackSizeEnvParseError`, `TestPackSizeEnvApplied`, and `TestPackSizeEnvIgnoredWhenFlagSet` cover `RESTIC_PACK_SIZE`. `TestCompressionEnvParseError`, `TestCompressionEnvApplied`, and `TestCompressionEnvIgnoredWhenFlagSet` cover `RESTIC_COMPRESSION`.

Control flow and state: tests use `t.Setenv`, temporary directories, pflag flag sets, and direct calls to unexported helpers in the same package. Flag `Changed` state is used to verify CLI overrides environment values.

Dependencies and integration points: uses restic `errors.IsFatal`, test helpers, `pflag`, and OS file APIs. It validates behavior consumed by all CLI commands.

Risks and test signals: tests protect user-facing configuration precedence and fatal error clarity. They do not cover backend opening, cache cleanup, password-command stderr behavior, or interactive terminal retries.
