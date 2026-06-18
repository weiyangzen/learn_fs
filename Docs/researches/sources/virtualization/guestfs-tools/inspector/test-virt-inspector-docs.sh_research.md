# File Research: sources/virtualization/guestfs-tools/inspector/test-virt-inspector-docs.sh

## Role

Documentation coverage test for `virt-inspector`.

## Behavior

The script sources `../tests/functions.sh`, enables `set -e` and `set -x`, honors `skip_if_skipped`, then runs top-level `podcheck.pl` against `virt-inspector.pod` and the `virt-inspector` tool name. It passes `--path $top_srcdir/common/options` so POD include directives for shared options can be resolved.

## Research Notes

This test ensures command-line options reported by the binary remain documented in the man page and help output.
