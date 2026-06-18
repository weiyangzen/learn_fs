# File Research: sources/os/plan9/9front/sys/src/cmd/disk/mkext.c

Extractor/listing tool for `mkfs -a` archive streams.

Key behavior:
- Reads archive headers from stdin: quoted name, mode, uid, gid, mtime, byte count.
- Stops on `end of archive`.
- Can extract files/directories, list headers with `-h`, preserve uid/gid with `-u`, preserve mtime with `-T`, set a destination prefix with `-d`, and filter selected paths.
- Creates needed parent directories for selected extraction.
- Verifies uid/gid/time preservation after writing when requested.

Notable dependencies:
- Plan 9 quoted string parsing and `Biobuf`.

Research notes:
- Archive file data follows each header immediately; skipped entries are consumed with `seekpast`.
- `error` exits with status `0`, matching some old Plan 9 tool conventions but surprising for fatal errors.
