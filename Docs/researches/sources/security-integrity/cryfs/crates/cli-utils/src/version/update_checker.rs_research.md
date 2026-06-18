## sources/security-integrity/cryfs/crates/cli-utils/src/version/update_checker.rs

Purpose: fetches and parses CryFS update/security-warning metadata from `https://www.cryfs.org/version_info.json`.

Important APIs and types: `check_for_updates(http_client, current_version)` returns `UpdateCheckResult` containing optional `released_newer_version` and optional `security_warning`. `VersionResponse` deserializes `version_info.current` and optional `warnings`. `parse_warning` selects a warning whose key exactly matches the running version string.

Control flow and state: the function performs a GET with a 2-second timeout, parses JSON with serde, parses the newest version, compares it to the current version, and returns a newer-version string only if the server version is greater. No state is persisted.

Dependencies and integration: uses the `HttpClient` trait, `serde_json`, `cryfs_version::Version`, and `anyhow`. `version.rs` calls it from `_maybe_check_for_updates`.

Risks and test signals: tests cover HTTP errors, invalid JSON, missing fields, invalid versions, newer/older versions, empty warnings, matching warnings, and warnings for other versions. Security warning matching depends on exact version string formatting, including prerelease/build metadata behavior.
