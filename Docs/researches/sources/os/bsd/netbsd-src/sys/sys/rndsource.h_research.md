# File Research: sources/os/bsd/netbsd-src/sys/sys/rndsource.h

Read completely: 102 lines.

This kernel-only header defines entropy-source registration and input APIs. It defines `rnd_delta_t` for time/value delta entropy estimation and `struct krndsource`, the driver-allocated per-source state carrying name, type, flags, cold entropy counters, callback pointers, and ABI-preserved unused fields.

Main APIs include `rndsource_setcb`, `rnd_attach_source`, `rnd_detach_source`, legacy `_rnd_add_uint32/_rnd_add_uint64`, and modern `rnd_add_uint32`, `rnd_add_data`, `rnd_add_data_intr`, and `rnd_add_data_sync`.

Risks: source structs are treated as opaque by drivers but contain ABI-preserved fields. Call-context matters: interrupt, sync, and generic data-add paths have different constraints.
