# File Research: sources/os/bsd/netbsd-src/sys/sys/kernhist.h

Defines optional kernel history tracing. It provides event/history structures, sysctl export formats, history category bitmasks, and macros that compile away when `KERNHIST` is disabled. When enabled, `KERNHIST_LOG` atomically reserves ring entries, timestamps them, records CPU/function/call/format/four values, and optionally prints immediately.

This is diagnostic infrastructure used by UVM, USB, bio, and other subsystems. Risks are ring overwrite behavior, format string lifetime, performance overhead when enabled, and ABI versioning for sysctl history export.
