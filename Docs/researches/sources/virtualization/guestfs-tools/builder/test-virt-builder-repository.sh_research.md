# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-repository.sh

## Scope

Slow integration test for `virt-builder-repository`.

## Behavior

- Creates a temporary repository test directory.
- Copies a Fedora phony image and writes a minimal index entry.
- Runs `virt-builder-repository` interactively with no compression, feeding architecture, name, osinfo, and expand device answers.
- Verifies generated index fields: revision, arch, name, osinfo, checksum, format, size, compressed size, and expand path.
- Adds a Debian image and reruns repository generation, ensuring new image metadata is added without changing Fedora revision.
- Modifies Fedora image via `virt-edit`, reruns with compression, and verifies revision increments, file becomes `.xz`, compressed image exists, and original raw image is removed.

## Dependencies And Risks

- Requires phony images, `virt-builder-repository`, `virt-edit`, and compression support.
- Interactive prompts are tested by piped input, so prompt ordering is part of the behavioral contract.
