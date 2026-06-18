## sources/security-integrity/cryfs/crates/cli-utils/src/version/version.rs

Purpose: prints the application version banner, local build warnings, and optional update/security information.

Important APIs and functions: `show_version` writes to stderr through `_show_version`. `warning` formats warning lines. `_maybe_check_for_updates` respects environment flags and calls `update_checker::check_for_updates` when enabled and interactive.

Control flow and state: `_show_version` prints `name version`, then emits warnings for development builds with commits after tag, uncommitted build trees, prerelease versions, and debug builds. With update checks enabled, it skips network access when `CRYFS_NO_UPDATE_CHECK=true` or noninteractive mode is active; otherwise it reports newer releases, server-provided security warnings, or update-check failure messages.

Dependencies and integration: uses `console::style`, `cryfs_version::{VersionInfo, Version}`, `Environment`, `HttpClient`, and `UpdateCheckResult`. `application.rs` invokes it during `--version`, normal startup, and parse-error handling.

Risks and test signals: tests capture output for release/prerelease/git-modified/development/debug scenarios, update-check disablement, newer-version messages, failures, and security warnings. A TODO notes `--version` should likely print to stdout instead of stderr. Network failures are nonfatal and reported as warnings.
