# File Research: sources/os/linux/linux-stable/fs/nfs/getroot.c

## Purpose

Obtains and installs the root dentry for an NFS mount from the mount root filehandle.

## Main Entry Points

- `nfs_superblock_set_dummy_root()`: creates an invisible dummy superblock root dentry for the NFS superblock.
- `nfs_get_root()`: fetches root attributes, gets the root inode, obtains the dentry, applies LSM mount options, and stores `fc->root`.

## Control Flow And State

`nfs_get_root()` duplicates the mount source string for possible dentry fsdata, allocates labeled fattrs, calls the protocol `getroot()` operation, turns the returned filehandle/attributes into an inode with `nfs_fhget()`, and ensures the superblock has a dummy root. The actual mount root is acquired with `d_obtain_root()`, security hooks instantiate it, and the source name is attached to root dentry fsdata when safe.

For cloned submounts, the function verifies the root is a directory and clones security mount options from the parent superblock. For ordinary mounts, it applies parsed security options. It also disables NFS security-label capability if the LSM did not accept native labels.

## Dependencies

Depends on protocol `getroot`, `nfs_fhget()`, NFS fattr allocation/security label handling, VFS dentry helpers, LSM superblock/dentry hooks, and mount context clone data.

## Risks

The dummy root deliberately removes itself from the inode alias list to avoid later dcache splicing problems during unmount. Error paths must release fattrs, root dentries, and the duplicated source name correctly. Security-label capability must reflect the final LSM mount-option result.
