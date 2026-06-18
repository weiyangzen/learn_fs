# sources/security-integrity/encfs/tests/config_v5_save_test.rs

Purpose: regression test ensuring V5 configs are not silently saved as V6 XML when their version field is modified.

Important APIs/types/functions: uses `EncfsConfig::load`, `EncfsConfig::save`, and `ConfigType::V5`. The single test is `test_v5_config_save_errors_correctly`.

Control flow: copies `tests/fixtures/encfs142/.encfs5` into a temp directory, loads it, asserts V5 type, mutates `version` to a newer V6-like value, then calls `save`. It expects an error containing "not yet implemented", asserts `.encfs6.xml` was not created, and verifies the original binary file does not start with an XML prolog.

State and persistence: creates a temp directory, copies a fixture, and removes the temp directory. It intentionally checks on-disk side effects after failed save.

Dependencies and integration points: depends on the V5 fixture and config save/load code. It protects the migration boundary between legacy binary configs and XML configs.

Risks: skips with `Ok(())` if the fixture is absent, so missing fixture coverage can hide regressions. The error-string assertion is brittle if wording changes.

Test signals: strong guard against destructive or misleading V5 save behavior.
