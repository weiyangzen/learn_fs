## sources/security-integrity/cryfs/crates/cli-utils/src/config.rs

Purpose: formats and prints CryFS filesystem configuration, including old-to-new value transitions after config loading/migration decisions.

Important APIs and functions: `print_config(&ConfigLoadResult)` prints filesystem format version, created-with version, last-opened-with version, cipher, block size, and filesystem id. Nested helpers `print_value`, `format_bytes`, `format_key`, and `format_value` handle changed-value display and terminal styling.

Control flow and state: the function writes directly to stdout. For unchanged values it prints one styled value; for changed values it prints `old -> new`. Byte values are formatted with binary units and raw byte counts.

Dependencies and integration: depends on `byte_unit`, `console::style`, and `cryfs_config::config::ConfigLoadResult`. CLI apps call it after config loading to inform the user about effective filesystem settings.

Risks and test signals: a TODO calls out missing integration tests for output. Since it is display-only, security risk is low, but inaccurate old/new reporting could mislead users during migrations or config mismatch diagnosis.
