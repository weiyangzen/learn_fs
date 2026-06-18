# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.h

This header declares the C wrapper callback symbols used by the Go binding.

Contents:
- Lifecycle wrappers: load, unload, dump_plugin, config, config_complete, get_ready, after_fork, preconnect.
- Connection wrappers: open, close, get_size, capability checks.
- I/O wrappers: pread, pwrite, flush, trim, zero.

Integration:
- Included by cgo blocks in `nbdkit.go` and `wrappers.go`.
- Function signatures match nbdkit API version 2 callback types.
