# sources/user-network-fs/nfs-utils/systemd/nfsroot-generator.c

Purpose: `nfsroot-generator.c` creates an initrd `sysroot.mount` unit for NFS root filesystems described on the kernel command line.

Important APIs and control flow: `get_nfsroot_info_from_cmdline` parses `/proc/cmdline` forms `root=/dev/nfs nfsroot=...` and dracut-style `root=nfs[4]:...`, deriving server from `ip=` when omitted and splitting path/options. `generate_sysroot_mount_unit` writes `sysroot.mount` with `_netdev`, `nofail`, `x-systemd.after=network-online.target`, and any provided options. `main` only emits units in initrd.

State, dependencies, and integration: It uses transient systemd generator output and depends on `/proc/cmdline`, initrd detection via `systemd_in_initrd`, and `systemd_escape` helpers.

Risks and test signals: Parsing is in-place and assumes `root` is non-null before `strcmp(root, "/dev/nfs")`; malformed cmdlines can return errors. Tests should cover both documented syntaxes, omitted server with `ip=`, option separators, non-initrd no-op, and malformed inputs.
