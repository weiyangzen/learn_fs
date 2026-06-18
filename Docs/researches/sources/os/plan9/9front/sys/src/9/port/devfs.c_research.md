# File Research: sources/os/plan9/9front/sys/src/9/port/devfs.c

Purpose: synthetic block-composition device `#k`, building file-system-like block devices from inner devices as mirrors, concatenations, interleaves, partitions, and encrypted devices.

Exposed interface: top-level trees under `#k`; default tree `#k/fs` always exists and contains `ctl`. Configured devices appear as files in trees. `ctl` accepts `mirror`, `cat`, `inter`, `part`, `crypt`, `clear`, `del`, and `disk`.

Core implementation: `Tree` stores named device directories; `Fsdev` stores type, size, start, inner devices, config name, qid version, refs, and optional AES-XTS key. `mconfig` parses one config line, opens inner devices under read lock, then adds/removes configuration under write lock. `rdconf` initializes `fs` and optionally reads a config file from `fsconfig` or `/dev/sdC0/fscfg`.

I/O paths: `catio` maps linear ranges across inner devices; `interio` stripes fixed 8 KiB blocks; `mirror` reads retry across copies and writes all copies with retry logging; `part` offsets into one inner device; `cryptio` encrypts/decrypts 512-byte sectors using AES-XTS after a default 64 KiB header offset. `mread`/`mwrite` clamp to device size and dispatch by type.

Lifecycle: `mopen` refs active devices, `mclose` decrefs or final-deletes gone devices, and `mdelctl`/`mdeldev` mark devices gone and free trees when safe. Config text is regenerated into `confstr`.

Dependencies: generic Chan I/O, sd allocation for crypt write buffers, AES-XTS from `libsec.h`, and kernel locking.

Research notes: main risks are nested device locking, deletion while open, mirror retry semantics, encryption alignment/key handling, config parsing, and correct close/free ordering outside locks.
