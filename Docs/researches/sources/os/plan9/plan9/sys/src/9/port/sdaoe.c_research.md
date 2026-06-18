# File Research: sources/os/plan9/plan9/sys/src/9/port/sdaoe.c

Implements an `sd` interface for ATA-over-Ethernet devices exposed through Plan 9 AoE paths.

Main model:
- `Ctlr` tracks AoE path, data channel, version/media-change flags, feature bits, SMART state, geometry, serial/firmware/model strings, and raw identify data.
- Controllers are kept in a global linked list protected by `ctlrlock`.
- `SDifc sdaoeifc` exports AoE as a storage interface named `"aoe"`.

Key behavior:
- `aoepnp` reads `aoedev` config entries and creates placeholder `SDev` instances.
- `pnpprobe` and `aoeprobe` issue `discover` to the AoE control file, wait for an `ident` file to appear, and create/link a controller.
- `aoeidentify` reads `<path>/ident`, parses ATA identify data, fills SD inquiry model fields, and updates geometry/version on media changes.
- `aoeonline` connects `<path>/data`, refreshes identity, and sets `SDunit` geometry; ATAPI path can delegate online handling to SCSI.
- `aoerio` handles SCSI-like read/write commands by translating command LBA/count into reads/writes on the AoE data channel.
- `sdfakescsi` handles generic fake SCSI requests before direct read/write translation.
- `aoerctl` reports model, serial, firmware, SMART, feature flags, and geometry.
- `aoeprobew`, `aoeclear`, `aoertopctl`, and `aoewtopctl` support dynamic probing and top-level control.

Cautions:
- `delctlr` loop advances with `x = c->next` instead of `x = x->next`; this looks suspicious and could break traversal if not intentional.
- Some ATAPI and cache-flush paths are stubbed or commented out.
