# File Research: sources/virtualization/nvme-cli/.github/workflows/checkpatch.yml

- Purpose: pull-request style review using kernel `checkpatch.pl`.
- Trigger: pull requests only.
- Key behavior: checks out the PR head with full history, downloads `checkpatch.pl` from Linux `master`, and pipes `git format-patch origin/${{ github.base_ref }}..HEAD` into it.
- Dependency: behavior is influenced by `.checkpatch.conf` in the repository root.
