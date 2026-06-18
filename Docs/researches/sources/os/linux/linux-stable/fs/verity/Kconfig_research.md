# File Research: sources/os/linux/linux-stable/fs/verity/Kconfig

Defines fs-verity configuration. `CONFIG_FS_VERITY` enables read-only file-based authenticity protection using a Merkle-tree mechanism analogous to dm-verity but per file. It depends on page size no larger than 64 KiB and selects SHA-256/SHA-512 library support and hash metadata.

The help text identifies supported filesystems as ext4, f2fs, and btrfs, and describes transparent read-time verification plus access to the root/file digest for auditing or authenticity workflows.

`CONFIG_FS_VERITY_BUILTIN_SIGNATURES` optionally adds in-kernel verification of builtin signatures and selects `SYSTEM_DATA_VERIFICATION`. The help warns that builtin signatures are not always the preferred trust model compared with userspace verification or IMA appraisal.
