# File Research: sources/virtualization/guestfs-tools/builder/test-website/virt-builder/repos.d/libguestfs.conf.in

## Scope

Test repository config for website/template list checks.

## Contents

- Defines `[libguestfs.org]`.
- Points to the signed local template index under `@abs_top_srcdir@/builder/templates/index.asc`.
- References the local `libguestfs.gpg` key.
- Notes it is only enough for commands like `--list` and does not contain installable templates.

## Risks And Invariants

- Configure substitutes the absolute source directory.
- Intended for metadata/listing tests, not actual template builds.
