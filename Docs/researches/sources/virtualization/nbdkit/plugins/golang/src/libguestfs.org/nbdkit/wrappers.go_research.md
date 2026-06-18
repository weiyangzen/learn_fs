# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.go

This file contains C wrapper functions embedded via cgo so nbdkit can call stable C symbols that forward into exported Go functions.

Key behavior:
- Defines `wrapper_*` functions for load, unload, dump_plugin, config, config_complete, get_ready, preconnect, open, close, get_size, capability checks, and I/O callbacks.
- Each wrapper calls the corresponding exported `impl*` Go function.
- Saves the original PID during load.
- `nonwrapper_after_fork` warns if the process has forked after loading a Go plugin.

Integration:
- `nbdkit.go` installs these wrapper function pointers into `struct nbdkit_plugin`.
- `wrappers.h` declares the wrapper symbols for cgo compilation.

Important note:
- The after-fork handler warns but currently returns success; a commented `return -1` shows stricter behavior was considered.
- This reflects the documented concern that Go plugins should not be used across forked processes.
