# File Research: sources/os/linux/linux/fs/vboxsf/Kconfig

## Purpose
Defines the kernel configuration option for VirtualBox guest shared-folder filesystem support.

## Main Contents
- `config VBOXSF_FS`: tristate option named “VirtualBox guest shared folder (vboxsf) support”.
- Depends on `(ARM64 || X86) && VBOXGUEST`.
- Selects `NLS`.
- Help text explains it implements the Linux guest side of folders exported by a VirtualBox host.

## Cross-File Relationships
- Controls compilation through `fs/vboxsf/Makefile`.
- Dependency on `VBOXGUEST` matches the wrapper layer’s use of VirtualBox guest HGCM services.

## Risks / Review Notes
- Architecture and guest-driver dependencies are essential; the source comments note assumptions around host data alignment and supported platforms.
