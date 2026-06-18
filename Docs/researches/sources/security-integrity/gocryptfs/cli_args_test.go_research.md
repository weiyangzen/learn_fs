# sources/security-integrity/gocryptfs/cli_args_test.go

Purpose: This test file locks down gocryptfs command-line parsing compatibility.

Important APIs and functions: `TestPrefixOArgs` verifies `-o` and `-o=` expansion, ordering, empty entries, and error handling. `TestConvertToDoubleDash` checks conversion from old single-dash long flags to pflag-style double dash while preserving `-h` and `--`. `TestParseCliOpts` checks selected parsed fields.

Control flow and state: Tests are table-driven and compare full argument slices or parsed `argContainer` values. They may depend on crypto backend preference helpers for OpenSSL defaults.

Dependencies and integration points: Protects user-facing CLI behavior and mount/fstab compatibility after parser changes.

Risks and test signals: The tests intentionally encode compatibility quirks, so changing behavior can be a regression even if pflag would parse it differently. Strong signals are exact transformed argument slices and expected parsed options.
