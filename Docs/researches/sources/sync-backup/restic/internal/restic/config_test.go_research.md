
# sources/sync-backup/restic/internal/restic/config_test.go

Purpose: tests config save/load round-trip through the generic unpacked repository interfaces.

It defines minimal `saver` and `loader` test doubles implementing `SaveUnpacked`, `LoadUnpacked`, and `Connections`. `TestConfig` creates a max-version config, saves it while asserting file type is `ConfigFile`, captures the serialized bytes, then loads from those bytes and asserts the original and loaded configs are equal.

State is captured in a local byte slice, not a backend. Integration points are `CreateConfig`, `SaveConfig`, `LoadConfig`, JSON helpers, and file-type routing. Risks covered include wrong file type use and serialization drift. It does not test invalid versions or polynomial validation failures.
