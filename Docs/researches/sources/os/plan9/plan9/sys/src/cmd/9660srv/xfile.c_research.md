# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/xfile.c

Purpose: 9660srv fid table and underlying image-device reference management.

Key behavior: `getxdata` opens/reuses image files by qid/type/dev identity; `putxdata` closes and purges cache on last reference. `refxfs` manages mounted filesystem references. `xfile` allocates, looks up, cleans, or clunks fid records in hash buckets with a freelist; `clean` releases filesystem and private ISO state.

Integration notes: `doclone`, attach, clunk, and error cleanup all depend on this file. There is a likely type-size typo in allocation of a free `Xdata` slot using `sizeof(Xfs)`, but layout may still be large enough by accident.
