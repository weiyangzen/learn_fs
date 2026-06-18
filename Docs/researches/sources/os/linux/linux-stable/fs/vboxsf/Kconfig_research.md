# File Research: sources/os/linux/linux-stable/fs/vboxsf/Kconfig

Defines `CONFIG_VBOXSF_FS`, the VirtualBox guest shared folder filesystem driver. It is tristate, depends on ARM64 or X86 plus `VBOXGUEST`, and selects NLS support for optional filename charset conversion.

The help text positions the driver as the Linux guest-side implementation for folders exported by VirtualBox hosts. It can be built-in or modular. Its dependency on `VBOXGUEST` reflects that all filesystem operations are mediated through the VirtualBox guest device and HGCM shared-folder service.
