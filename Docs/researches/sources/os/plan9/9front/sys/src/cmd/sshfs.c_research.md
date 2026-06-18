# File Research: sources/os/plan9/9front/sys/src/cmd/sshfs.c

`sshfs.c` implements a Plan 9 9P filesystem backed by SFTP v3 over an SSH subprocess or supplied stdin/stdout.

Architecture:
- Defines SFTP v3 packet types, open flags, attribute flags, and status codes.
- `SFid` stores remote path, SFTP handle, qid, and buffered directory entries per 9P fid.
- `SReq` wraps queued 9P requests and close-handle work.
- Request IDs are allocated from a bounded `MAXREQID` table; `sendproc` serializes queued SFTP writes, while `recvproc` matches replies back to pending requests.

Major behavior:
- `sshfsattach` maps attach names to root-relative, absolute, or home-relative paths.
- `sshfswalk` computes path candidates and issues remote `STAT`.
- `sendproc` maps 9P attach/walk/open/create/read/write/stat/wstat/remove to SFTP `STAT`, `OPEN`, `OPENDIR`, `READDIR`, `READ`, `WRITE`, `SETSTAT`, `RENAME`, `REMOVE`, and `RMDIR`.
- `recvproc` translates SFTP `STATUS`, `HANDLE`, `DATA`, `NAME`, and `ATTRS` into 9P responses.
- Directory reads buffer `Dir` records, skip `.` and `..`, and synthesize stable qid paths by SHA-1 hashing remote path strings.
- `readfile` fetches `/etc/passwd` and `/etc/group`-style files for uid/gid name maps.

Mount/startup:
- `threadmain` supports read-only mode, debug, post-only `-p`, command mode `-c`, service/mount options, uid/gid map files, and root path.
- Normally spawns `/bin/ssh ... #sftp`; `-p` uses existing fds.

Risks:
- SFTP v3 has weaker metadata semantics than 9P; qids are synthesized and may not track remote file identity across rename/recreate.
- `dir2attrib` notes deliberate spec violation for `-1` uid/gid “don’t change” behavior used by OpenSSH.
- The request-id limit bounds concurrency to 32 outstanding SFTP operations.
