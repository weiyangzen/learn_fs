# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumphdr.h

This header defines the on-device crash dump header format, dump metadata structures, compression stream metadata, and kernel dump subsystem entry points.

Key contents:
- Dump constants: magic, version, word size, panic string size, conservative compression ratio, device padding offset, saved log area size, ereport area size, and summary area size.
- `dumphdr_t`: crash dump header containing offsets to symbols, PFN table, translation map, dump data, utsname/platform/panic/time metadata, page geometry, hash metadata, page counts, symbol sizes, fault-management panic flag, and OS image UUID.
- Dump validity/content flags:
  - `DF_VALID`
  - `DF_COMPLETE`
  - `DF_LIVE`
  - `DF_COMPRESSED`
  - `DF_KERNEL`
  - `DF_ALL`
  - `DF_CURPROC`
  - `DF_CONTENT`
- `dump_map_t` and `DUMP_HASH()` for translating address-space/virtual-address pairs to dump data offsets.
- Compressed-size/tag word encoding helpers:
  - `DUMP_SET_TAG`
  - `DUMP_GET_TAG`
  - `DUMP_SET_CSIZE`
  - `DUMP_GET_CSIZE`
- Parallel dump stream metadata `dumpstreamhdr_t` and stream magic `DUMP_STREAM_MAGIC`.
- Data-header metadata `dumpdatahdr_t`, magic/version constants, and compression-level constants for LZJB and bzip2.
- Kernel-only globals for dump vnode, dump size, dump header, config flags, path, timeout/error state, and platform CPU thresholds.
- Kernel dump functions such as `dumpinit`, `dumpfini`, `dump_resize`, `dump_page`, `dump_addpage`, `dumpsys`, helper variants, log/ereport dump routines, dump device writes/resizing, platform dump hooks, and UUID accessors.
- Dump-page reservation helpers and `IS_DUMP_PAGE()`.

Dependencies:
- Includes `sys/types.h`, `sys/param.h`, `sys/utsname.h`, and `sys/log.h`.
- Kernel section depends on vnode, mutex, PFN/page, and address-space types.
- Uses C++ guards.

Research notes:
- The file documents the two-header dump layout: one header at the beginning and a terminal header at the end of the dump device.
- Struct layout and constants are savecore/dumpsys compatibility boundaries.
- Storage relevance is direct: this describes how kernel memory images are laid out on dump devices and how compressed dump streams are interpreted.
