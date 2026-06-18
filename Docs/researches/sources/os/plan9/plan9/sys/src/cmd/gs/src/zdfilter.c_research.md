# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdfilter.c

Implements a small PostScript interface for device filter stack management.

The sole operator, `.popdevicefilter`, calls `gs_pop_device_filter()` using stable memory and the current graphics state.

The includes are largely copied from `zdevice.c`, but the only functional dependency beyond interpreter/device basics is `gsdfilt.h`.

Registered in `zdfilter_op_defs`.
