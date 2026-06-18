# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/suntpi.h

`suntpi.h` defines private kernel support for Transport Provider Interface capability caching. It is for sockfs and timod internal use.

`tpi_provinfo_t` records provider entries keyed by opaque data, protected by a mutex because the capability bitfields are not atomic. It tracks whether capability, local-name, and peer-name operations are supported, unsupported, or unknown using the two-bit values `PI_DONTKNOW`, `PI_NO`, and `PI_YES`.

Kernel declarations initialize the cache (`tpi_init()`), find provider information from a queue (`tpi_findprov()`), lock/unlock provider entries, and allocate TPI acknowledgement messages (`tpi_ack_alloc()`).
