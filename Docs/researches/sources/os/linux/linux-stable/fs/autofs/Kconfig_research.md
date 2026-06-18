# File Research: sources/os/linux/linux-stable/fs/autofs/Kconfig

## Purpose
Defines the `AUTOFS_FS` kernel configuration option for kernel automounter support.

## Main Contents
`AUTOFS_FS` is a tristate option named “Kernel automounter support (supports v3, v4 and v5)”. The help text explains that autofs works with userspace automounter tools, reduces overhead for already-mounted paths, and builds as module `autofs` when selected as `M`.

## Risks / Review Notes
This is configuration metadata only. It does not define dependencies beyond user guidance, but enabling it exposes the autofs filesystem and `/dev/autofs` control interface compiled from the accompanying sources.
