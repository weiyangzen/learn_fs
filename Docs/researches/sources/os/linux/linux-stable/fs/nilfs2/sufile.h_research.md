# File Research: sources/os/linux/linux-stable/fs/nilfs2/sufile.h

`sufile.h` declares the segment usage file interface. It exposes segment count/clean count accessors, allocation range setup, single-segment allocation, dirty marking, segment usage updates, stats and suinfo get/set operations, resize, sufile inode loading, and fstrim handling.

The generic update APIs accept callbacks that receive the sufile inode, segment number, header block, and usage block. The header declares callback primitives for scrap, free, cancel-free, and set-error operations.

Inline wrappers define the common operations used elsewhere: `nilfs_sufile_scrap()` makes a segment garbage/dirty, `nilfs_sufile_free()` frees one segment, `nilfs_sufile_freev()` frees multiple segments, `nilfs_sufile_cancel_freev()` re-dirties segments whose freeing is being rolled back, and `nilfs_sufile_set_error()` permanently marks a segment erroneous.

The comments make the error model explicit for `set_error`: invalid segment, metadata I/O/corruption, and allocation failure. The header depends on `mdt.h` because sufile is implemented as a NILFS metadata file.
