# sources/test-tools/fio/oslib/libmtd_legacy.c

Purpose: pre-sysfs MTD support for older Linux kernels using `/proc/mtd` and MTD ioctls.

Important APIs/functions: `legacy_libmtd_open()`, `legacy_dev_present()`, `legacy_mtd_get_info()`, `legacy_get_dev_info()`, and `legacy_get_dev_info1()`. Internal `proc_parse_start()` reads `/proc/mtd`; `proc_parse_next()` parses device number, size, erase size, and quoted name.

Control flow: the parser reads the whole `/proc/mtd` buffer, validates the header, and advances line by line. Device info validates a node is a character device with major `90`, opens it, reads `MEMGETINFO`, probes `MEMGETBADBLOCK`, validates geometry, maps MTD type constants to strings, derives `mtd_num` from the minor, and then re-parses `/proc/mtd` for the device name.

State and persistence: no persistent library state beyond caller structs; it opens and closes device/proc files. It probes but does not modify device state except through ioctls that should be informational.

Dependencies and integration: Linux MTD UAPI, `/proc/mtd`, `/dev/mtd%d`, and common MTD helpers. Called by `libmtd.c` when sysfs support is unavailable.

Risks: legacy kernel assumptions are old and hard to test. `legacy_dev_present()` returns early without freeing the parser buffer when it finds a match, leaking memory. Error paths depend on exact `/proc/mtd` formatting. Device node requirements may fail on systems without static `/dev/mtd*` nodes.

Test signals: mocked `/proc/mtd` parser cases and integration on an old or simulated MTD setup.
