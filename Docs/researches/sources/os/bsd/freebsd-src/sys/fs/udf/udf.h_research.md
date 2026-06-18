# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf.h

Internal FreeBSD UDF filesystem state and helper interface header.

Key responsibilities:
- Defines `struct udf_node`, the per-vnode UDF object holding vnode, mount, hash ID, lookup offset, and copied file entry.
- Defines `struct udf_mnt`, the per-mount state for GEOM consumer/device, buffer object, block geometry, partition bounds, root ICB, sparing table, and optional disk-to-local iconv handle.
- Defines `struct udf_dirstream` for directory FID iteration, including buffer, offset, fragmentation, and error state.
- Defines file-handle structure `ifid`, conversion macros `VFSTOUDFFS` and `VTON`, device block read helpers, and `udf_getid`.
- Declares vnode allocation, tag validation, vnode lookup, UMA zones, and FIFO ops.

Dependencies:
- Depends on UDF on-disk structures from `ecma167-udf.h` and FreeBSD vnode, mount, buffer, GEOM, and UMA facilities.
- `udf_readdevblks` depends on mount block size/mask initialization and `RDSECTOR`.

Notable risks:
- `udf_getid` uses only the logical block number from a long allocation descriptor, matching the implementation’s limited partition model.
- `udf_readdevblks` guards negative and overflowing sizes, but callers still need valid media-derived sizes.
- The mount state supports sparing tables and one partition path, not the full UDF partition model.
