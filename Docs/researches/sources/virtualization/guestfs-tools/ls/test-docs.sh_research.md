# File Research: sources/virtualization/guestfs-tools/ls/test-docs.sh

## Role

Documentation coverage test for `virt-ls`.

## Behavior

The script runs `podcheck.pl` against `virt-ls.pod` and `virt-ls`, passing the shared options path. It ignores aliases/options `--checksums`, `--extra-stat`, `--time`, and `--uid`, which are accepted by the tool but intentionally handled specially for documentation parity.

## Research Notes

This keeps the rich `virt-ls` option surface synchronized with its POD and help output.
