# sources/sync-backup/kopia/repo/local_config_test.go

Purpose: tests local repository config persistence and loading edge cases.

Important APIs/types/functions: `TestLocalConfig_withCaching`, `TestLocalConfig_noCaching`, `TestLocalConfig_notFound`, and `mustParseJSONFile`.

Control flow: temporary config files are written through `writeToFile`, raw JSON is inspected, and `LoadConfigFromFile` is used to verify loaded values. Missing-file behavior checks `os.ErrNotExist` wrapping.

State/persistence behavior: creates temporary config files and verifies cache directories are stored relative but loaded as absolute.

Dependencies/integration: uses `testutil.TempDirectory`, `ospath.IsAbs`, `content.CachingOptions`, JSON decoding, and `testify/require`.

Risks/test signals: protects config portability across moved config directories. It does not cover environment overrides, permissive cache loading gate, or file permissions.
