# File Research: sources/os/bsd/netbsd-src/sys/sys/device.h

Public NetBSD autoconfiguration and device framework header.

Key content:
- Device classes: generic, CPU, disk, network, tape, tty, audio, display, bus, virtual.
- Device activation enums and typedefs for `device_t`, `cfdata_t`, `cfdriver_t`, `cfattach_t`.
- `devhandle_t` abstraction for ACPI/OpenFirmware/FDT/OpenBoot/private handles.
- Device compatibility entries and handle implementation types.
- Device call registration macros and descriptors.
- Configuration data structures: locators, interface attributes, parents, `cfdata`, `cftable`, `cfattach`, `cfdriver`, `cfattachinit`.
- Attach declaration macros and detach flags.
- Search/attach argument structure `cfargs` and `CFARGS` helper.
- Kernel APIs for config initialization, attach/detach, deferred config, device lookup/refcounting, registration, properties, compatibility matching, power management, iteration, shutdown traversal, and generic device calls.

Important behavior:
- Separates public framework contracts from private layout in `device_impl.h`.
- Device property API supports typed access and defaults for data, strings, booleans, and integer sizes.
- Core header for driver attachment and runtime device tree operations.
