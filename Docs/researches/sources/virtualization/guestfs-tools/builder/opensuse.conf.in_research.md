# File Research: sources/virtualization/guestfs-tools/builder/opensuse.conf.in

## Scope

Default virt-builder repository configuration template for openSUSE images.

## Contents

- Defines `[opensuse.org]` with an openSUSE Virtualization repository image index URL.
- References the installed `opensuse.gpg` key under `@SYSCONFDIR@/virt-builder/repos.d`.

## Risks And Invariants

- Uses HTTP for the repository URI while relying on GPG key verification for integrity.
- Configure substitutes `@SYSCONFDIR@`.
