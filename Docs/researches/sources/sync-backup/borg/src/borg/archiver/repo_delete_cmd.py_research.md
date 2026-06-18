# sources/sync-backup/borg/src/borg/archiver/repo_delete_cmd.py

## Purpose

`repo_delete_cmd.py` implements `borg repo-delete`, deleting an entire repository and its local cache/security metadata, or deleting only the local cache. It includes a strong confirmation path for destructive repository deletion. The source was read as a complete 133-line file.

## Important APIs, Types, and Functions

`RepoDeleteMixIn.do_repo_delete()` opens the repository exclusively without a manifest, optionally loads the manifest to count/list archives, asks for `YES` confirmation through `yes()`, calls `repository.destroy()`, optionally calls `SecurityManager.destroy(repository)`, and always destroys `Cache` unless dry-run. `build_parser_repo_delete()` registers `--dry-run`, `--list`, counted `--force`, `--cache-only`, and `--keep-security-info`.

## Control Flow

If `--cache-only` is not set and no `--force` is supplied, the command builds a confirmation message containing repository ID, location, and optionally archive listings. It handles missing manifests by warning that contents cannot be described. The user must type exact `YES`, or set `BORG_DELETE_I_KNOW_WHAT_I_AM_DOING`, otherwise `CancelledByUser` is raised. Non-dry-run destroys the repository and security info unless kept, then destroys the cache. Dry-run logs what would happen.

## State and Persistence Behavior

Non-dry-run repository deletion removes repository storage; cache deletion removes local cache state; security info deletion removes local security metadata unless `--keep-security-info` is set. `--cache-only` leaves the repository and security info alone but deletes cache. Dry-run performs no deletion.

## Dependencies and Integration Points

The module depends on repository destruction, `Cache.destroy()`, `SecurityManager.destroy()`, manifest loading/listing, archive formatting, `yes()` confirmation, and `NoManifestError`. It is the hard-delete counterpart to archive-level `delete` and `prune`.

## Risks and Edge Cases

`--force` bypasses the interactive archive listing/confirmation path. Missing or corrupt manifest means the command cannot enumerate contents but can still delete the repository. `--keep-security-info` can leave local metadata behind intentionally. Cache destruction occurs after repository deletion path and also in cache-only mode, so tests must separate those branches.

## Test Signals

Tests should cover dry-run with and without cache-only, confirmation success/failure, environment override, archive listing in confirmation, missing-manifest confirmation text, forced deletion, security-info deletion and preservation, cache-only deletion, and repository/cache destroy call ordering.
