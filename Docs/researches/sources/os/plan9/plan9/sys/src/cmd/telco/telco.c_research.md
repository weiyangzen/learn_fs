# File Research: sources/os/plan9/plan9/sys/src/cmd/telco/telco.c

A user-level 9P file server that exposes modem devices under `/net/telco` for data and fax use.

Key responsibilities:
- Publishes `/srv/telco`, mounts itself under `/net`, and serves a hierarchy containing `telco`, `clone`, per-modem directories, `data`, and `ctl`.
- Tracks Fids, queued read requests, modem devices, circular receive buffers, ownership, and permissions.
- Implements 9P handlers for version, attach, walk, open, read, write, clunk, stat, and wstat.
- Treats writes to `ctl` beginning with `connect ` as dial requests; other control writes pass through to the serial device control file.
- Monitors modem input in per-device background processes, buffering incoming bytes and auto-answering RING events when enabled.
- Detects modem type/speed, applies Hayes-style commands, configures data or fax class, dials numbers, receives calls, and starts service programs.
- Supports modem-specific command tables for Rockwell, AT&T, MultiTech, and Vocal variants.

Important behavior:
- The filesystem uses simple permission emulation rather than reading `/adm/users`.
- `clone` picks a free modem and redirects the opened fid to that modem's `ctl`.
- `data` reads can be deferred by queuing a `Request`; `serve()` replies later when monitor input arrives.
- Incoming data calls exec `/bin/service/telcodata`; fax calls exec `/bin/service/telcofax`.
- `onhook()` toggles serial control lines and reinitializes the modem for fax-capable answering.

Notable risks:
- `serve()` compares `r->count` to `sizeof(buf)`, where `buf` is a pointer, so large reads can be truncated to pointer size.
- The receiver child passes `dev->t->name` instead of `d->t->name`, which likely reports the first device's modem type.
- Protocol, modem command timing, circular-buffer state, and 9P reply ordering are tightly coupled.
- `rflush()` removes queued reads but does not appear to send an explicit flushed read response for a removed request.
