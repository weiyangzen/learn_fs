# File Research: sources/os/plan9/9front/sys/src/9/boot/disk.proto

Prototype extension adding local disk filesystem support to boot images.

Key contents:
- Includes filesystem servers/tools: `9660srv`, `dossrv`, `cfs`, `cwfs64x`, `gefs`, `hjfs`.
- Includes disk tools: `cryptsetup`, `edisk`, `fdisk`, `prep`, `fstype`, and `diskparts`.
- Installs `local.rc` boot method.
- Creates `lib/firmware`.

Role:
- Enables local-disk discovery and mounting during boot.
