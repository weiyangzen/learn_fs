# File Research: sources/virtualization/guestfs-tools/sparsify/test-virt-sparsify-docs.sh

Documentation/CLI consistency test for `virt-sparsify`.

Key behavior:
- Sources shared test functions and honors skip environment.
- Runs `podcheck.pl` against `virt-sparsify.pod` and command `virt-sparsify`.
- Adds common options include path.
- Ignores `--inplace`, likely because the documented or aliased form differs from CLI naming.

Research notes:
- No disk images are created; this is documentation validation only.
