# File Research: sources/os/plan9/plan9/sys/src/9/port/devfs.c

Implements `#k/fs`, a kernel block/file composition device rather than an on-disk filesystem. It builds synthetic devices from other files/devices using mirror, concatenation, interleaving, and partition mappings.

The top-level namespace contains trees, with the default persistent tree `fs`. Tree/device qids encode tree number and device number. `Fsdev` records type, name, tree, size, start offset, permissions, and inner devices. `Inner` records the opened backing channel, name, and size. `Tree` groups configured devices under a directory.

Configuration is through `#k/fs/ctl` or an optional boot config file (`fsconfig`, default `/dev/sdC0/fscfg` if present). Commands include `mirror`, `cat`, `inter`, `part`, `disk`, `clear`, and `del`. The `disk` command sets default tree, sector size, and optional default source for sd-style partition commands.

Reads and writes are dispatched by device type. `catio` maps sequential spans across inner devices. `interio` stripes fixed `Blksize` chunks across devices. `part` offsets into one inner device. `mirror` reads from the first successful copy and writes to all copies, retrying transient failures up to `Maxretries`.

Configuration changes are protected by a global `RWlock`; active I/O holds read locks, while add/delete holds write locks. Deletion marks devices gone and defers final free until open references drain. Backing channels are opened while only holding a read lock to permit nested `#k` devices.

Notable behavior: permissions are the intersection of inner device permissions; interleaved devices truncate inner sizes to block boundaries; partition starts/sizes are scaled by current sector size. This is a compact software RAID/partition layer for Plan 9 device files.
