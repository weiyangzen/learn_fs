# File Research: sources/os/linux/linux-stable/fs/adfs/super.c
- Purpose: Implements ADFS mount, superblock operations, option parsing, disc record validation, inode cache, and module lifecycle.
- Main functions: `adfs_checkdiscrecord`, `adfs_parse_param`, `adfs_reconfigure`, `adfs_statfs`, `adfs_probe`, `adfs_validate_bblk`, `adfs_validate_dr0`, `adfs_fill_super`, `adfs_init_fs_context`, module init/exit.
- Mount flow: Parses owner/group/mask/filetype suffix options, probes for disc records, reads and validates the map, selects F or F+ directory ops, creates the root inode/dentry, and sets default dentry operations.
- Super operations: Allocate/free/drop inodes, write inodes, put super, statfs, and show mount options.
- Integration: Registers the `adfs` filesystem type and uses block-device mount support through `get_tree_bdev`.
- Risks: Disc record validation protects against invalid geometry and oversized media; mount cleanup must release maps and buffers on partial failure.
