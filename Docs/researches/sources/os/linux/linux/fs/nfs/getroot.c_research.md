# File Research: sources/os/linux/linux/fs/nfs/getroot.c

## Purpose
Gets and installs the root dentry for an NFS mount from the mount root filehandle.

## Main Flow
`nfs_get_root()`:
- Duplicates `fc->source` for possible storage in root dentry `d_fsdata`.
- Allocates an NFS fattr with security label support.
- Calls protocol `getroot()` using the mount filehandle.
- Converts the root filehandle/fattr into an inode with `nfs_fhget()`.
- Obtains a root dentry via `d_obtain_root()`.
- Instantiates security state on the dentry.
- Stores the mount source name in root `d_fsdata` when appropriate.
- Sets `s->s_root` and `fc->root`.
- Applies or clones LSM mount options.
- Clears `NFS_CAP_SECURITY_LABEL` if LSM mount options do not preserve native labels.
- Applies inode security label data with `nfs_setsecurity()`.

## Clone/Reconfigure Behavior
When cloning from an existing superblock, it verifies the root inode is an NFS directory and clones security mount options from the parent superblock. It also copies `has_sec_mnt_opts` from the clone source server.

## Error Handling
Failure paths release fattrs, source-name storage, and root dentries as needed. Errors are reported through `nfs_errorf()` with mount-context-visible messages.

## Research Notes
This is the root installation point after mount context and server setup. It ties together protocol root getattr, inode creation, dentry setup, security labels, and superblock root assignment.
