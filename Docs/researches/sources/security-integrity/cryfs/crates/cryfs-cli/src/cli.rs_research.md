<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/cli.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/cli.rs

Purpose: main CLI application implementation that connects parsed args, logging, config/local-state checks, and runner mounting.

Important APIs/types/functions: `Cli` implements `cryfs_cli_utils::Application`. Key methods are `new`, `default_log_config`, `should_show_version`, `defer_logging_init`, `main`, `daemon_default_log_config`, `async_main`, `sanity_checks`, `run_filesystem`, `show_ciphers`, `load_or_create_config`, `config_file_location`, `check_config_integrity`, `mount_args`, `password_provider`, and `console`.

Control flow: `main` first handles hidden daemon mode, then `--show-ciphers`, then selects foreground/background `Mounter`. Background mode resolves daemon logging before runtime startup. Async flow checks directories, loads or creates config, prints config, translates FUSE/atime options, calls `mount_filesystem`, and prints unmount notice for foreground.

State and persistence: may create vault/mount dirs, create/load/rewrite encrypted config files, update local filesystem metadata, and update vaultdir-to-filesystem-id metadata.

Dependencies/integration: integrates `cryfs_config`, `cryfs_runner`, `cryfs_cli_utils`, `cryfs_blockstore`, `clap_logflag`, and `InteractiveConsole`.

Risks/test signals: error mapping is extensive but many TODOs remain for user-facing error messages and mount tests. `allow_replaced_filesystem` parameter is forwarded into config loading and checked again for vaultdir metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/cli.rs -->
