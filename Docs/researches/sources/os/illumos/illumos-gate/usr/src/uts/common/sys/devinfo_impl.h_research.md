# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devinfo_impl.h

This private/public-adjacent header defines the devinfo driver ioctl flags and the snapshot data structures copied to userland/libdevinfo. It is separate from `libdevinfo.h` because the devinfo driver must know copy sizes before libdevinfo is built.

The ioctl namespace is `DIIOC`. Snapshot flags request subtree, minor data, properties, I/O pathing, private data, force-load all drivers, cached data, cleanup, layering, and hotplug data. Straight ioctl commands include userland copyout, load driver, and identify. `DI_MAGIC` is returned by identify.

Snapshot format constants include operation kind bits, property list kinds, max tree depth, private pointer count, snapshot version, private-data version, endian constants, cache magic, cache permissions, and cache snapshot flags. Cast macros convert offsets/pointers to snapshot structure types.

The snapshot structures include `di_all`, `di_devnm`, layered link endpoint/linkage structures, `di_node`, `di_minor`, `di_path`, `di_hp`, `di_path_prop`, `di_prop`, private data formatting records, aliases, and `dinfo_io`. These encode exported node metadata, minor nodes, properties, pathing/multipath state, hotplug state, layering, and private prtconf support.

`di_path_state_t` defines unknown, offline, standby, online, and fault path states. Path snapshot flags indicate missing endpoints, endpoint postprocessing, missing client/phci links, and link postprocessing. Removed-device path flags mirror device removal state.

Research notes:
- This is an ABI-sensitive snapshot format for libdevinfo/devinfo driver coordination.
- Many fields are offsets into a copied snapshot rather than live kernel pointers.
- Version constants and structure sizes must be preserved for cached snapshots and mixed user/kernel consumers.
