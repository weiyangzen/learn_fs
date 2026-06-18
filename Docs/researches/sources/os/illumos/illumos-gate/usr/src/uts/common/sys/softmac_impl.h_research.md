# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac_impl.h

## Role

Private implementation header for softmac, the compatibility layer that registers legacy DLPI network devices with the GLDv3/MAC framework.

## Key Contents

Defines lower-stream receive callback types, `softmac_lower_t`, softmac attachment state, per-minor `softmac_dev_t`, softmac flags, and the central `softmac_t` object. `softmac_t` tracks device identity, attach/detach state, hold counts, minor nodes, MAC handle, DLPI media/style/address/SDU properties, notification capabilities, checksum/capability flags, active/fastpath state, notify thread queues, lower stream, and upper stream list.

Defines ioctl start control structures and datapath mode constants for unknown, slowpath, and fastpath. Defines `softmac_upper_t` for upper STREAMS instances, including task queue linkage, associated lower stream, pending DLPI messages, fastpath state, flow control, direct RX callbacks, and MAC TX notify callback.

## Interfaces

Declares DLPI request helpers, init/fini, fastpath init/fini, capability enable/fill, receive processing, output, MAC provider entry points, hold/release, lower setup, active/fastpath controls, datapath switching, and upper stream write/close routines.

## Design Notes

The header documents several locking domains: per-softmac mutexes, active mutex, fastpath mutex, upper dispatch mutex, and upper fastpath mutex. Fastpath/slowpath switching is a major design concern.
