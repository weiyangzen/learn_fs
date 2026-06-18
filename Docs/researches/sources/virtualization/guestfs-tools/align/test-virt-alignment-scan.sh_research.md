# File Research: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan.sh

## Scope

Direct-image smoke test for `virt-alignment-scan`.

## Behavior

- Runs the tool on `../test-data/phony-guests/fedora.img` with `--format=raw`.
- Accepts alignment-result exit codes `0`, `2`, and `3`.

## Dependencies And Risks

- Requires the Fedora phony guest image.
- Does not validate exact partition alignment text, only successful execution and recognized result codes.
