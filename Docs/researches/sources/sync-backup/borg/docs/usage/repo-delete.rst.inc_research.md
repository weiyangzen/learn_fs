# sources/sync-backup/borg/docs/usage/repo-delete.rst.inc

Purpose: Documents `borg repo-delete`, which deletes an entire repository or only its local cache.

Important APIs/types/functions: CLI contract is `borg [common options] repo-delete [options]`. Options include `--dry-run`, `--list`, `--force` with repeat escalation, `--cache-only`, and `--keep-security-info`.

Control flow: Runtime either deletes only local cache, or enumerates and deletes repository contents, local cache, and security info unless options say otherwise. `--dry-run --list` previews targets.

State and persistence: Destructive mutation of repository storage and local security/cache state. `--keep-security-info` preserves local security metadata; `--cache-only` leaves repository storage intact.

Dependencies and integration points: Integrates with repository backends, cache management, security info storage, and archive listing.

Risks: Irreversible repository deletion. Corrupted archives may require force escalation. Users need dry-run/list preview to avoid deleting the wrong repository.

Test signals: Cover dry-run output, cache-only behavior, security-info retention/removal, force levels for corrupted repos, remote/local repositories, and refusal/confirmation paths if implemented outside this help text.
