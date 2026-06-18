# sources/security-integrity/cryfs/crates/check/src/cli.rs

Purpose: This file implements the `cryfs-check` CLI application and the public `check_filesystem` entrypoint used by tests or callers.

Important APIs and flow: `RecoverCli` implements `Application` with name/version/logging, creates a multi-thread Tokio runtime, prints the target vault path, builds an `OnDiskBlockStore`, uses `InteractivePasswordProvider`, calls `check_filesystem`, prints each `CorruptedError`, then prints a count. `check_filesystem` wraps the blockstore in `ReadOnlyBlockStore`, loads config read-only, prints config, sets up the blockstore stack, and invokes `RecoverRunner` as a `BlockstoreCallback`.

State and persistence: The intended blockstore access is read-only, but a TODO notes read-only blockstore may not be sufficient to prevent local-state or integrity-data writes. Config is loaded through `cryfs_config::config::load_readonly` with command-line flags that treat missing blocks as not integrity violations.

Dependencies and integration: It depends heavily on `cryfs_cli_utils`, `cryfs_config`, `cryfs_blockstore`, `cryfs_utils::progress`, and `RecoverRunner`. Integrity config currently allows violations so the checker can continue collecting corruption diagnostics.

Risks and test signals: Noninteractive password handling is not implemented, custom config paths are TODO, integrity violation callback is empty, and exit codes are not specialized. `RecoverConsole` contains TODO methods that can panic if config loading requires migration or other prompts.
