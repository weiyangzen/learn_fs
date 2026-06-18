# File Research: sources/os/plan9/9front/sys/src/9/port/devaoe.c

Purpose: Plan 9 kernel AoE initiator device, exposed as `#æ/aoe`, implementing ATA-over-Ethernet discovery, device registration, config I/O, identify, and sector reads/writes.

Exposed interface: top-level `ctl` and `log`; per-AoE-unit directories named `<major>.<minor>` with `ctl`, `data`, `config`, `ident`, and `devlink/` entries. Top-level control commands include `bind`, `unbind`, `discover`, `rediscover`, `autodiscover`, `debug`, and deprecated `remove`. Unit control commands include `failio`, `identify`, `jumbo`, `maxbno`, `mtu`, `nofail`, and `setsize`.

Core implementation: maintains global `devs`, `netlinks`, event ring, unit counters, and per-device `Aoedev` state with `Devlink` paths, outstanding `Frame`s, SRB queues, config/identify data, negotiated MTU, open count, and flags. `aoesweepproc` periodically rediscover/resends timed-out frames and adapts RTT/window/MTU behavior. `netrdaoeproc` reads AoE packets from bound Ethernet channels and dispatches config, ATA, and error responses.

Important paths: `rw` creates SRBs for sector-aligned data I/O; `strategy`, `work`, and `atarw` split requests into AoE frames; `atarsp` completes frames and wakes SRBs; `qcfgrsp` creates/updates devices and links; `configwrite` sends AoE config writes; `netbind`/`netunbind` attach and detach Ethernet AoE readers.

Dependencies: Plan 9 device framework, Ethernet/netif, IP headers, AoE protocol definitions, ATA identify helpers from `fis.h`, kernel locking, rendezvous, block queues, and configured `aoeif`.

Research notes: this is a complex, stateful storage path. Review should focus on lock ordering around `devs`, `Aoedev`, and `netlinks`; frame/SRB lifetime; resend behavior under `nofail`; MTU/jumbo fallback; and unbind/remove races with outstanding I/O.
