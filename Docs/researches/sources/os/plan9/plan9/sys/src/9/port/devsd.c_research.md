# File Research: sources/os/plan9/plan9/sys/src/9/port/devsd.c

Purpose: Generic Plan 9 storage device file server for `#S/sd*`. It discovers `SDifc` controllers, exposes controller/unit directories, partition files, control files, and raw SCSI request access.

Key logic:
- Maintains global storage-device slots named by digits/letters and adds `SDev` chains from each registered `SDifc`.
- Lazily verifies units with `ifc->verify`, enables controllers, initializes unit metadata, and creates default `data` plus boot-configured partitions.
- Encodes dev/unit/partition/type into `Qid.path` and implements attach, walk, stat, open, read, write, wstat, configure, and unconfigure.
- `sdbio` maps partition byte I/O to sector-aligned `ifc->bio` calls, including read-modify-write for unaligned writes.
- `sdrio` and the `raw` file implement direct SCSI-like command/data/status exchange through `ifc->rio`.
- `sdfakescsi`, `sdsetsense`, and `sdmodesense` emulate common SCSI commands for non-SCSI disk drivers.
- Top-level `sdctl` dispatches modern `wtopctl` commands and a legacy `config` parser for controller probing/removal.

Dependencies and integration:
- Depends on `../port/sd.h`, generated `sdifc[]`, Plan 9 device helpers, `DevConf`, partition permission state, and driver callbacks such as `pnp`, `probe`, `enable`, `disable`, `verify`, `online`, `bio`, `rio`, `rctl`, and `wctl`.

Risks and notes:
- `sdbio` has subtle media-change recovery and locking differences for removable vs non-removable media.
- Raw command state is serialized per unit and exclusive-opened.
- Partition `qid.vers` combines unit and partition versions to detect media/partition changes.
- `sdgetdev` can return nil; one error path calls `decref` after nil detection, which is suspicious.
