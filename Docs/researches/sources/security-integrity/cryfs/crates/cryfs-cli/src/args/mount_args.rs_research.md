<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mount_args.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mount_args.rs

Purpose: clap parser for mount-mode arguments and flags.

Important APIs/types/functions: `MountArgs` includes positional `vaultdir` and `mountdir`, optional config path, foreground/background selection, create-missing flags, integrity-violation flags, filesystem upgrade/replacement allowances, cipher and blocksize expectations, idle unmount duration, and repeated `-o/--fuse-option` values. `parse_byte_amount` parses `byte_unit::Byte`.

Control flow: clap validates required positionals and cipher possible values. `Cli` later maps these flags into config loading and runner mount arguments.

State and persistence: no direct persistence. Flags influence vault/mount directory creation, config rewrite, local-state checks, and mount behavior in other modules.

Dependencies/integration: uses `cryfs_cli_utils::parse_path`, `cryfs_config::config::ALL_CIPHERS`, `humantime`, `byte_unit`, and `FuseOption`.

Risks/test signals: unit tests cover human duration parsing and binary/decimal byte parsing. Several TODOs note defaults should be dynamic and replaced-filesystem scenarios need deeper tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mount_args.rs -->
