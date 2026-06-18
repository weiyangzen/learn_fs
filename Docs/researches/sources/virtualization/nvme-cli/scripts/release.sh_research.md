# File Research: sources/virtualization/nvme-cli/scripts/release.sh

Release automation script.

Key elements:
- Accepts `VERSION` plus flags to skip docs, force sanity checks, or skip library dependency update.
- Validates versions like `v2.1`, `v2.1.0`, or pre-release forms such as `-rc.0`.
- Registers cleanup that deletes created tags and resets to the original HEAD unless release completes.
- Requires clean tree and `master` branch unless forced.
- Optionally regenerates docs via `scripts/update-docs.sh` and commits them.
- Updates `meson.build` version with `sed`, commits, creates a signed tag, dry-runs push, then asks before pushing.

Notes:
- Uses destructive git operations in cleanup (`git reset --hard`) by design for release rollback.
- Mentions `dry_run` in a branch although no `dry_run` variable is defined in this file.
