# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.h

## Purpose

`lfs_inode.h` defines the LFS/ULFS in-memory inode structure used by the kernel and by userland LFS tools running in a faked kernel environment. It also defines inode state flags, lookup-result state, LFS-specific inode extension state, quota constants, debug logging hooks, and helper macros.

## Main Data Structures

`struct ulfs_lookup_results` records directory lookup side effects: free-slot size, useful directory end, lookup hint offset, free-space offset, and found record length. LFS rename code consumes this state between lookup and directory mutation.

`struct inode` combines generic vnode/genfs state, mount/device identity, state flags, quota pointers, NFS modrev, lockf state, cached lookup results, LFS extension pointer, cached dinode fields, directory hash state, and the backing `union lfs_dinode *`.

`struct lfs_inode_ext` holds LFS-only volatile state: on-disk file size, effective block count pending I/O, direct-block fragment sizes, dirop/paging/cleaning list links, LFS private flags, highest logical block, kernel-only block-allocation splay tree, truncation segment-delta rb tree, and cleaner-preserved on-disk link count.

## Important Flags

`i_state` includes generic inode timestamp/write flags (`IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFY`, `IN_MODIFIED`, `IN_ACCESSED`) and LFS-specific lifecycle flags such as `IN_CLEANING`, `IN_ADIROP`, `IN_PAGING`, `IN_CDIROP`, and `IN_MARKER`. `IN_ALLMOD` groups all states requiring inode writeback.

`lfs_iflags` includes `LFSI_NO_GOP_WRITE`, `LFSI_DELETED`, `LFSI_WRAPBLOCK`, `LFSI_WRAPWAIT`, and `LFSI_BMAP`, controlling page-write behavior, deleted-inode flushing, wrap control, and bmap state.

## Integration Notes

The header deliberately mirrors pieces of UFS inode state while adding LFS log-cleaning and segment-accounting state. Accessor macros such as `i_lfs_effnblks`, `i_lfs_fragsize`, `i_lfs_lbtree`, and `i_lfs_segdhd` hide the extension pointer layout from implementation files.

## Debug Support

Under `DEBUG`, this file defines the circular Ifile write log structure, `LFS_BWRITE_LOG`, `LFS_ENTER_LOG`, and `DLOG_*` debug categories. Without debug, these collapse to direct writes or no-ops, preserving call sites without runtime logging overhead.
