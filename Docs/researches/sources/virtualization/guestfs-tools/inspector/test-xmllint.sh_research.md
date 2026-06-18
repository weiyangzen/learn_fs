# File Research: sources/virtualization/guestfs-tools/inspector/test-xmllint.sh

## Role

Schema validation test for checked-in example XML files.

## Behavior

The script sources the common test functions, enables strict/trace shell mode, honors skips, and runs `$XMLLINT --noout --relaxng $srcdir/virt-inspector.rng` for every `$srcdir/example-*.xml`.

## Research Notes

Unlike the phony-image tests, this validates static example XML files, ensuring documentation/sample outputs remain compatible with the inspector Relax NG schema.
