# File Research: sources/os/plan9/9front/sys/src/cmd/srvfs.c

`srvfs.c` is a small helper that posts an `exportfs` instance into `/srv` for a path.

Behavior:
- Usage: `srvfs [-dR] [-p perm] [-P patternfile] [-e exportfs] srvname path`.
- Builds an argument vector for `/bin/exportfs` or a replacement specified with `-e`.
- Supports exportfs flags:
  - `-d`
  - `-R`
  - `-P patternfile`
  - Always adds `-r path`.
- Creates a pipe, posts one end into `/srv/<srvname>` or an absolute service path with `ORCLOSE`, then forks a child that dup’s the other pipe end to stdin/stdout and execs exportfs.
- `-p` controls service file permissions, default `0600`.

Integration:
- Uses Plan 9 service-file convention: writing an fd number to `/srv/...`.
- Uses `rfork(RFPROC|RFNOWAIT|RFNOTEG|RFFDG)` so the exportfs child persists independently.

Risks:
- Fixed `arglist[16]` is adequate for current options but not dynamically checked.
- `buf[64]` bounds service path expansion; long service names are truncated by `snprint`/`strecpy` behavior.
