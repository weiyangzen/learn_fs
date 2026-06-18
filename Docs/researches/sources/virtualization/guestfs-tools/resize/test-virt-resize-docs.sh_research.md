# File Research: sources/virtualization/guestfs-tools/resize/test-virt-resize-docs.sh

Documentation/CLI consistency test for `virt-resize`.

Key behavior:
- Sources shared test functions and skips through `skip_if_skipped`.
- Runs `podcheck.pl` against `virt-resize.pod` and command `virt-resize`.
- Ignores spelling/option aliases: `--LVexpand`, `--lv-expand`, `--lvexpand`, and `--dryrun`.

Research notes:
- This validates option documentation against command-line help, not runtime resize behavior.
