# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast.h

`hast.h` is the central HAST public/internal header for resource configuration, protocol constants, roles, and runtime state.

Key definitions:
- Protocol version history and current `HAST_PROTO_VERSION` 2.
- HAST error codes for control responses.
- Control command IDs.
- Roles: undefined, init, primary, secondary.
- Sync source IDs.
- HAST I/O operation IDs: read, write, delete, flush, keepalive.
- Default user, paths, timeout, control socket, listen addresses, pidfile, extent size, keepdirty, address size, token size, and keepalive interval.
- Replication modes: fullsync, memsync, async.
- Compression modes: none, hole, lzf.
- Checksum modes: none, crc32, sha256.

Main structs:
- `hastd_listen`: listen address plus proto connection.
- `hastd_config`: control address/connection, pidfile, listen list, resource list.
- `hast_resource`: comprehensive per-resource configuration and runtime state.

`hast_resource` includes:
- Names, replication/compression/checksum settings, protocol version, exec hook.
- Local provider path/fd/offset/data size/media size/sector size/flush settings.
- GEOM Gate descriptor and unit.
- Remote/source addresses, inbound/outbound proto connections, token, timeout.
- Resource ID and local/remote modification counters.
- Role/previous role, worker pid, parent-worker control/event/connection channels.
- Activemap pointer and locks.
- I/O and error statistics.
- Worker-specific status callback.
- TAILQ linkage.

This file is the shared contract across parser, daemon, worker, protocol, and control code.
