# File Research: sources/os/linux/linux/fs/hfsplus/ioctl.c

## Role

Implements HFS+-specific ioctl handling. The only supported ioctl is boot “blessing”.

## Key Functions

- `hfsplus_ioctl_bless(struct file *file, int __user *user_flags)`
  - Requires `CAP_SYS_ADMIN`.
  - Uses the file dentry and inode to reach the HFS+ superblock private state and active/backup volume headers.
  - Reads the bootloader CNID from `dentry->d_fsdata`.
  - Under `sbi->vh_mutex`, updates `finder_info` in both primary and backup volume headers:
    - `finder_info[0]`: parent directory containing the bootable system;
    - `finder_info[1]`: bootloader CNID, using dentry filesystem data so hard links bless the hard-link file ID rather than the indirect inode;
    - `finder_info[5]`: OS X system folder, set to the same parent directory value.
  - The `user_flags` pointer is accepted by signature but not read.
- `hfsplus_ioctl(struct file *file, unsigned int cmd, unsigned long arg)`
  - Dispatches `HFSPLUS_IOC_BLESS`.
  - Returns `-ENOTTY` for unsupported ioctl commands.

## Dependencies

Uses capability checks, VFS dentry/inode helpers, user pointer types, and HFS+ volume header state from `hfsplus_fs.h`.

## Research Notes

The ioctl updates in-memory volume header copies only. Persistence depends on normal HFS+ superblock commit/sync paths writing the primary and backup headers later.
