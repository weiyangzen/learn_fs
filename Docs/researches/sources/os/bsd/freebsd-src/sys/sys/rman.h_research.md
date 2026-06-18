# File Research: sources/os/bsd/freebsd-src/sys/sys/rman.h

Read completely: 165 lines.

## Purpose
Defines the kernel resource manager interface for reserving, activating, adjusting, and exporting bus/device resource ranges.

## Main Elements
- Defines resource flags for allocated, active, shareable, first-share, prefetchable, optional, unmapped, and encoded alignment.
- Defines `enum rman_type`, `RM_TEXTLEN`, maximum resource end, and default-range test macro.
- Defines userspace-exported `struct u_resource` and `struct u_rman` snapshots.
- Under `_KERNEL`, defines public ABI-sensitive `struct resource` with opaque implementation pointer plus bus tag/handle fields.
- Defines `struct rman` with resource list, mutex, global list linkage, managed start/end, type, and description.
- Declares resource activation/deactivation, adjustment, free-region lookup, bus tag/handle/device/flag/rid/type/virtual/mapping accessors, init/fini/manage-region, reserve/release, alignment flag creation, and setters.
- Declares global `rman_head`.

## Dependencies And Integration
Used by bus/device drivers, machine bus space/resource definitions, resource sysctl/debug export, and device resource allocation/activation paths.

## Risk Notes
`struct resource` field offsets are explicitly device-driver ABI. Resource range and sharing flags must remain consistent with bus allocation/activation semantics.
