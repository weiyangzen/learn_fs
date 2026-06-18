# File Research: sources/local-fs/xfsprogs/db/bmroot.c

Defines field layouts and dynamic offset/count callbacks for inode-rooted btrees stored inside inode forks. It covers data and attr bmap btree roots (`bmrootd`, `bmroota`) and newer realtime metadata inode roots for rtrmap and rtrefcount btrees. For bmap roots, callbacks compute key and pointer counts/offsets from `xfs_bmdr_block_t` and fork sizes. For realtime metadata roots, callbacks switch between leaf records and internal keys/ptrs based on root level.

Size functions report the current inode fork size in bits. This file is purely structural decoding for inode-contained roots, but it depends heavily on current cursor data being the inode and on libxfs max-record/address helpers.
