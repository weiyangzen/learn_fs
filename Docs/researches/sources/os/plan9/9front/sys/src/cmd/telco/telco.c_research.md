# File Research: sources/os/plan9/9front/sys/src/cmd/telco/telco.c

`telco.c` implements a user-space 9P filesystem over serial modem devices. It publishes `/net/telco`, `clone`, per-device directories, and per-device `data`/`ctl` files, while also monitoring rings and dispatching incoming fax/data calls.

Major structures:
- `Fid`: tracks 9P fid state, qid, open state, and user.
- `Dev`: tracks real modem ctl/data fds, device type, file permissions, buffered input ring, pending read requests, and monitor process state.
- `Request`: queued blocked data reads.
- `Type`: modem type descriptors and command strings.

Filesystem model:
- Qids encode level/type and device index.
- `devgen()` enumerates root, `/telco`, `clone`, device directories, and `data`/`ctl`.
- `devstat()` synthesizes Plan 9 `Dir` metadata.
- `rversion`, `rattach`, `rwalk`, `ropen`, `rread`, `rwrite`, `rclunk`, `rstat`, and `rwstat` implement 9P operations.
- Opening `clone` assigns a free modem and returns its control file qid.

Modem behavior:
- `monitor()` opens real serial ctl/data files and forks a background reader.
- `attention()`, `apply()`, and `readmsg()` issue Hayes commands and parse modem responses.
- `modemtype()` probes modem speed/type and configures data/fax mode.
- `dialout()` parses `connect number[!speed][!nocompress][!fax]`, configures the modem, dials, and adjusts serial speed if needed.
- `receiver()` answers `RING`, distinguishes data versus fax by modem response, and execs `/bin/service/telcodata` or `/bin/service/telcofax`.
- `onhook()` toggles modem control lines and reinitializes fax-capable mode.

Buffered I/O:
- `monitor()` writes serial input into a circular `rbuf`.
- `rread()` queues `Request` objects for data reads.
- `serve()` drains pending read requests when bytes are available.

Risk notes:
- `serve()` allocates `buf = malloc(messagesize-IOHDRSZ)` but compares `r->count > sizeof(buf)`, which is pointer size, not allocation size; this can artificially limit reads and is suspicious.
- Permission logic assumes Plan 9 user/group conventions described in the comment rather than parsing `/adm/users`.
- Modem command handling is highly device-specific and depends on old Hayes/fax behavior.
