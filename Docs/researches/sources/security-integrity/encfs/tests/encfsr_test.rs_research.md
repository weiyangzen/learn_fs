# sources/security-integrity/encfs/tests/encfsr_test.rs

Purpose: non-live CLI regression tests for the `encfsr` binary. They validate help/version output, argument parsing, config validation, and progress to mount-attempt code without requiring a working FUSE mount.

Important APIs/types/functions: `encfsr_bin`, `write_test_config`, `copy_std_fixture`, `write_v7_config`, `write_valid_encfsr_config`, and `run_encfsr`. Config helpers construct V6 PBKDF2 and V7 Argon2 configs with deterministic key material. Tests cover `--help`, `--version`, missing source directory, missing config file, rejection of `unique_iv=true`, acceptance of chained name IV when `unique_iv=false`, passthrough FUSE opts after `--`, and absence of the old "not yet implemented" placeholder.

Control flow: helpers create temp dirs/configs, spawn `encfsr` with optional stdin password, collect stdout/stderr, and assert status and error text. Some tests intentionally use missing source or mount directories so execution fails at a known validation/mount step.

State and persistence: writes temporary config files/directories and cleans them. It does not mount or require live environment.

Dependencies and integration points: depends on Cargo binary path, `EncfsConfig::standard_v7`, `set_v7_key`, config save, PBKDF2 derivation, and clap-style CLI parsing.

Risks: stderr substring assertions are brittle. Some helpers are dead code but document alternate config paths. Tests that expect a mount-attempt failure rely on the absence of a mount directory rather than mocking FUSE.

Test signals: guards user-facing reverse-mode CLI contract and config gating, especially `unique_iv=false` acceptance and trailing FUSE option parsing.
