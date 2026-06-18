# File Research: sources/os/linux/linux/fs/coda/symlink.c

## Purpose
Implements Coda symlink page-cache reads by asking Venus for the symlink target.

## Main Elements
- `coda_symlink_filler()`: obtains the inode's Coda fid, calls `venus_readlink()`, stores the target text into the folio, and completes the folio read.
- `coda_symlink_aops`: exports `.read_folio` for symlink inodes.

## Dependencies And Integration
Used by Coda symlink inode setup elsewhere in the Coda filesystem. It depends on `ITOC()` for inode-private fid lookup and `venus_readlink()` from `upcall.c`.

## Risk Notes
The read buffer is a single page and `venus_readlink()` caps and NUL-terminates returned data. Folio completion uses the Venus result directly; failure leaves the folio not uptodate.
