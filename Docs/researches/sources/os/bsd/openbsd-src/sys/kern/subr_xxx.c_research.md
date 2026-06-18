# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_xxx.c

Contains small generic kernel helper stubs and device-number conversion routines.

Error/null helpers are straightforward: `enodev()` returns `ENODEV`, `enxio()` returns `ENXIO`, `eopnotsupp()` returns `EOPNOTSUPP`, and `nullop()` returns success. These are commonly used as operation-table placeholders.

`bdevsw_lookup()` returns the block-device switch entry for `major(dev)`. `chrtoblk()` maps character device numbers to corresponding block device numbers using `chrtoblktbl`, validating character major bounds and returning `NODEV` for missing mappings. `blktochr()` scans `chrtoblktbl` to convert a block device major back to a character device major.

`assertwaitok()` verifies the current context is allowed to sleep. It skips checks during panic or DDB, asserts IPL is `IPL_NONE`, asserts not in an SMR critical section, and under diagnostics panics if the current CPU holds mutexes.

Filesystem relevance: block/character device conversion is important for storage device paths, raw/block device handling, mount/root-device selection, and driver tables. `assertwaitok()` is also used by allocation and wait paths, including `pool_get(PR_WAITOK)`.
