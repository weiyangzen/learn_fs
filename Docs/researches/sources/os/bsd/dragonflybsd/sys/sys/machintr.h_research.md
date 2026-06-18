# File Research: sources/os/bsd/dragonflybsd/sys/sys/machintr.h

Kernel-only machine-independent interrupt ABI. Defines `machintr_type`, vector setup/teardown constants, and `struct machintr_abi` containing callbacks for interrupt enable/disable/setup/teardown, legacy interrupt routing, MSI/MSI-X allocation/release/map, finalization, stabilization, IRQ map initialization, and resource manager setup.

Storage and filesystem code do not call this directly, but block/network drivers depend on this interrupt abstraction underneath I/O completion.
