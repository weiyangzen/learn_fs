# File Research: sources/virtualization/guestfs-tools/builder/libguestfs.conf.in

## Scope

Default virt-builder repository configuration template for libguestfs-hosted indexes.

## Contents

- Defines `[libguestfs.org]` using `https://builder.libguestfs.org/index.asc`.
- Defines `[archive.libguestfs.org]` using `http://archive.libguestfs.org/builder/index.asc`.
- Both entries reference the installed `libguestfs.gpg` key under `@SYSCONFDIR@/virt-builder/repos.d`.

## Risks And Invariants

- `@SYSCONFDIR@` is substituted by configure.
- These repositories are network-backed and signature-checked through the configured GPG key.
