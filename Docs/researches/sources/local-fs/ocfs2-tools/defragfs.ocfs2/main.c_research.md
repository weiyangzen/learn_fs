# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/main.c

## Role

`defragfs.ocfs2/main.c` implements the online OCFS2 file defragmenter. It validates targets, walks directories, invokes the OCFS2 move-extents ioctl, tracks progress, and supports interrupted-run resume records.

## Target Handling

Targets may be block devices, directories, or regular files. Block devices are resolved to their first OCFS2 mount point through `/etc/mtab`. Files/directories are verified to be on an OCFS2 filesystem using `statfs64()` and `OCFS2_SUPER_MAGIC`, and directory targets use `nftw64()` with `FTW_PHYS | FTW_MOUNT` to avoid symlink following and crossing mounts.

## Defrag Operation

Regular files are skipped if empty, blockless, not owned by the current non-root user, not regular, or under `lost+found`. Defragmentation opens the file read-write and calls `ioctl(fd, OCFS2_IOC_MOVE_EXT, &me)` with `OCFS2_MOVE_EXT_FL_AUTO_DEFRAG` over the file size.

## Modes

`-c` counts candidate regular files, `-v` enables detailed output, `-l` periodically yields the scheduler, `-g` resumes from a stored record, and `-h` prints help. Progress is printed per file with success/failure counts.

## Resume Behavior

The traversal periodically stores a resume record every `RECORD_EVERY_N_FILES` or when SIGTERM/SIGINT sets `should_stop`. On resume, the tool skips entries until the stored inode is seen, then continues.

## Risk Areas

The man page and implementation differ for `-v`: code still defragments in detail mode. Resume by inode number can be fragile if directory contents change. The tool prints version on every run and uses `/etc/mtab`, which may be less authoritative than `/proc/self/mounts` on modern systems.
