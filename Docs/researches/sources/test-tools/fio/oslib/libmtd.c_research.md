# sources/test-tools/fio/oslib/libmtd.c

Purpose: imported mtd-utils library code used by fio for Linux Memory Technology Device discovery and operations.

Important APIs/functions: public APIs include `libmtd_open()`, `libmtd_close()`, `mtd_dev_present()`, `mtd_get_info()`, `mtd_get_dev_info()`/`mtd_get_dev_info1()`, `mtd_lock()`, `mtd_unlock()`, `mtd_erase()`, `mtd_regioninfo()`, `mtd_is_locked()`, `mtd_torture()`, `mtd_is_bad()`, `mtd_mark_bad()`, `mtd_read()`, `mtd_write()`, `mtd_read_oob()`, `mtd_write_oob()`, `mtd_write_img()`, and `mtd_probe_node()`. Internal helpers read sysfs attributes, parse major/minor files, convert device type strings, validate eraseblock offsets, and probe 64-bit ioctl availability.

Control flow: `libmtd_open()` constructs `/sys/class/mtd/...` path patterns and checks sysfs support; if unsupported, it falls back to legacy `/proc/mtd` behavior. Discovery scans sysfs `mtdX` directories, reads attributes such as `name`, `type`, `erasesize`, `writesize`, `subpagesize`, `oobsize`, and flags, and populates `mtd_dev_info`. Operation functions validate eraseblock numbers and offsets before issuing Linux MTD ioctls such as `MEMLOCK`, `MEMUNLOCK`, `MEMERASE64`/`MEMERASE`, `MEMGETREGIONINFO`, `MEMISLOCKED`, `MEMGETBADBLOCK`, `MEMSETBADBLOCK`, `MEMWRITE`, and OOB read/write variants. 64-bit ioctl support is discovered lazily by trying the 64-bit ioctl and falling back on `ENOTTY`.

State and persistence: `struct libmtd` stores allocated path patterns and a cached `offs64_ioctls` state. Operations persistently modify hardware state: eraseblocks may be erased, locked/unlocked, marked bad, written, or tortured with patterns.

Dependencies and integration: depends on Linux MTD UAPI (`<mtd/mtd-user.h>`), sysfs, `/proc/mtd` legacy support, `libmtd_int.h`, `libmtd_common.h`, and xalloc wrappers. fio uses it for MTD-aware test targets.

Risks: many functions are destructive by design. `mtd_torture()` appears to return `-1` even after a successful torture pass, which is suspicious despite logging success. `mtd_read()` loops while `rd < len` but calls `read(fd, buf, len)` each time rather than advancing `buf` and shrinking the remaining count, risking overwritten buffers or infinite loops on short reads. Sysfs parsing assumes small bounded files and exact kernel formats. Hardware operations require correct privileges and real devices.

Test signals: unit tests can mock sysfs/proc parsing, but integration needs MTD devices or loopback/simulated MTD. Critical tests should cover 64-bit ioctl fallback, bad-block operations, OOB bounds validation, alignment checks, and the `mtd_torture()` return contract.
