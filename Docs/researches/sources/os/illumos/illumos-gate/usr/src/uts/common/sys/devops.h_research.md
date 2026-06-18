# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devops.h

This header defines the core illumos driver operation vectors: `cb_ops`, `bus_ops`, legacy `bus_ops_rev1`, and `dev_ops`. It is the main contract between device drivers/nexus drivers and the kernel DDI framework.

`cb_ops` describes character/block/STREAMS leaf operations such as open, close, strategy, print, dump, read, write, ioctl, devmap, mmap, segmap, chpoll, prop_op, STREAMS tab pointer, flags, revision, aread, and awrite. Comments identify which entries correspond to DDI/DKI and obsolete interfaces.

`bus_ops` describes nexus operations: map, get/add/remove intrspec legacy hooks, DMA map/allochdl/freehdl/bind/unbind/flush/window/control, prop_op, ctl, DMA control legacy op, bus quiesce/unquiesce/bus reset/device reset, FMA init/fini/access enter/access exit/error handler, power, configure/unconfigure, and interrupt operations. Revision constants run through `BUSO_REV_10`.

`bus_ops_rev1` is retained for old busops layout compatibility. `dev_ops` stores revision, refcount, getinfo, identify, probe, attach, detach, reset, cb_ops pointer, bus_ops pointer, power, and quiesce.

Enums define getinfo command, attach commands, detach commands, and reset commands. Probe result constants map to familiar `ENXIO`/`nulldev` behavior. `DDI_DEFINE_STREAM_OPS` builds a `dev_ops`/`cb_ops` pair for STREAMS drivers.

Research notes:
- This file is one of the most ABI-sensitive headers in the DDI.
- Bus operation revision gates availability of newer callbacks such as `bus_intr_op`.
- Legacy fields remain in structure layout even when comments say obsolete.
