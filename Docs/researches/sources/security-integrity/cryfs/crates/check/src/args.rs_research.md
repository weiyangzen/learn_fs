# sources/security-integrity/cryfs/crates/check/src/args.rs

Purpose: This file defines the command-line argument struct for `cryfs-check`. `CryfsRecoverArgs` currently accepts one positional vault directory path.

Important APIs and flow: The struct derives `clap::Parser` and has `vaultdir: PathBuf` with `value_parser=parse_path`, delegating path parsing behavior to shared CLI utilities.

State and persistence: It stores only user input. The path later determines the on-disk blockstore root and `cryfs.config` path used by the CLI.

Dependencies and integration: It integrates with `cryfs_cli_utils::run::<RecoverCli>()` through the `Application` trait implementation in `cli.rs`.

Risks and test signals: The argument surface is intentionally small; TODOs elsewhere indicate config path customization and noninteractive password handling are not yet exposed here.
