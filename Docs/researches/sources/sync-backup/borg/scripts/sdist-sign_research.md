# sources/sync-backup/borg/scripts/sdist-sign

Purpose: Builds a source distribution and creates an armored detached signature for a specified Borg release version.

Important APIs/types/functions: Reads release version from `$1`, chooses `gpg` or `qubes-gpg-client-wrapper` depending on `QUBES_GPG_DOMAIN`, runs `python -m build`, then signs `dist/borgbackup-$R.tar.gz` with local user `Thomas Waldmann` into `$D.asc`.

Control flow: If version argument is empty, prints usage and exits. Otherwise chooses GPG command, builds distributions, computes expected sdist path, and signs it.

State and persistence: Writes build artifacts under `dist/` and signature file `dist/borgbackup-<version>.tar.gz.asc`.

Dependencies and integration points: Requires Python build frontend, project packaging metadata, GPG or Qubes GPG wrapper, and the maintainer signing key. Integrates with release publishing.

Risks: No `set -euo pipefail`; build or signing failures depend on shell exit behavior but the script does not explicitly validate artifact existence. Version argument must match the generated sdist filename exactly.

Test signals: Dry-run in release environment by building expected sdist, verify signature with public key, test both regular GPG and Qubes wrapper paths, and confirm failure behavior when version/artifact/key is missing.
