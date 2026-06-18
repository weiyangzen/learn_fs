# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-cacheall.sh

## Scope

Test for `virt-builder --cache-all-templates`.

## Behavior

- Creates temporary repo, config, and cache directories.
- Creates fake raw and qcow2 images with `qemu-img`.
- Computes checksums and writes a minimal native index with two entries and revisions.
- Configures `VIRT_BUILDER_DIRS` and `XDG_CACHE_HOME`.
- Verifies `virt-builder --list` exact output.
- Runs `virt-builder --cache-all-templates` and checks cached template filenames include OS, arch, and revision.

## Dependencies And Risks

- Requires `qemu-img`, checksum helper, and local filesystem URI support.
- Exact `--list` formatting is part of the test contract.
