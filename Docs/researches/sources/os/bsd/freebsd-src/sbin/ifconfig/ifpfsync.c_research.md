# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifpfsync.c

`ifpfsync.c` implements ifconfig support for pfsync interfaces. It registers commands for `syncdev`/`syncif`, `syncpeer`, `maxupd`, `defer`, and `version`, plus an `af_pfsync` status callback.

The module communicates with the kernel using nvlist payloads packed into `ifr.ifr_cap_nv` and sent through `SIOCGETPFSYNCNV` or `SIOCSETPFSYNCNV`. `pfsync_do_ioctl()` packs the input nvlist, allocates an ioctl buffer, calls the ioctl, destroys the old nvlist, and unpacks the returned nvlist.

`syncpeer` values are represented as nested nvlists containing address family and binary sockaddr data. Helpers convert between `sockaddr_storage` and nvlist form for IPv4/IPv6 when enabled.

Setters read the current nvlist, replace or clear the relevant key, and write the nvlist back. `maxupd` is range checked to 0-255; `version` is deliberately left to kernel validation.

`pfsync_status()` reads `syncdev`, `syncpeer`, `maxupdates`, `version`, and `flags`, then prints sync device, peer when non-default, defer state, version, and syncok state.

Risk notes: `pfsync_do_ioctl()` assumes packing, allocation, and buffer sizing succeed before `memcpy()`. It returns positive `EIO` on unpack failure while callers generally test only for `-1`, so error propagation is inconsistent in that path.
