# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4srv.c

Plan 9 9P file server front end for the ext4 library. It exposes mounted ext filesystems through a 9P `Srv`, maps Plan 9 file requests to ext4 operations, handles user/group permissions through a passwd/group-style table, and provides a command pipe for stats, sync, and halt.

Key behavior:
- `Aux` stores per-fid state: partition pointer, effective uid, path, directory offset, open ext4 file/dir handle, type, and remove-on-close flag.
- `haveperm` converts Plan 9 open modes to read/write/execute bits and checks other/owner/group permissions against ext4 inode mode, uid/gid, and parsed groups.
- `rattach` chooses the requested partition or default device partition, applies `-S` root override behavior, and creates the root fid.
- `ropen`, `rcreate`, `rread`, `rwrite`, `rremove`, `rstat`, `rwstat`, `rwalk1`, `rclone`, and `rdestroyfid` implement the 9P server operations using ext4 API calls.
- Directory reads use `dirread9p` and skip `.`/`..` plus unsupported entry types.
- Writes explicitly zero-fill holes up to the requested offset before writing, then honors append mode.
- `rwstat` supports rename, truncation, mode/append/tmp flags, mtime, and gid changes with Plan 9-style permission checks.
- `cmdsrv` posts `#s/<srvname>.cmd` and accepts `stats`/`df`, `sync`, and `halt`.
- `threadmain` parses service, debug, device, group, mkfs, block size, inode size, label, stdio, and root-override flags.

Notable dependencies:
- Uses public ext4 API from `include/ext4.h`, inode accessors, `group.c`, and partition/device helpers from `common.h`/other ext4srv files.
- Uses Plan 9 libraries: `fcall.h`, `thread.h`, `9p.h`, and `bio.h`.

Research notes:
- The server only exposes regular files and directories during walk and directory enumeration; symlinks and special files are effectively hidden from normal traversal.
- Permission checks treat root and group membership through the parsed group table, not through host OS credentials.
- Directory creation relies on `ext4_dir` embedding `ext4_file` as its first field when assigning qids through the union-backed pointer.
