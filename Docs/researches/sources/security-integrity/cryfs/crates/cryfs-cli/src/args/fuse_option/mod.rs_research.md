<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/mod.rs

Purpose: combines supported FUSE mount options into a single clap value enum.

Important APIs/types/functions: `FuseOption` wraps `AtimeOption` or `FusePermissionOption`. Its manual `ValueEnum` implementation returns all variants and delegates possible-value rendering. `partition` splits a mixed slice into atime options and permission options using `itertools::partition_map`.

Control flow: clap parses `-o/--fuse-option` values into this enum. `Cli::run_filesystem` partitions the values, validates atime behavior, and converts permission options for the runner.

State and persistence: no persistence. Values are transient CLI configuration.

Dependencies/integration: ties together local `atime_option` and `permission_option` modules, `clap::ValueEnum`, and `itertools`.

Risks/test signals: an assertion checks the manual variant list matches the sub-enum counts. If a new option is added but not included in `value_variants`, the assertion catches it at runtime when clap queries variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/mod.rs -->
