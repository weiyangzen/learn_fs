# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/platform.h

Purpose: Xen public dom0 platform-operation ABI. It defines `xen_platform_op` and subcommands for host clock, MTRR/memory types, microcode, EFI runtime calls, firmware information, ACPI sleep, CPU frequency/idle/power management, CPU online/offline/hot-add, memory hot-add, and core parking.

Key interfaces:
- `XENPF_INTERFACE_VERSION`.
- Payloads such as `xenpf_settime`, `xenpf_add_memtype`, `xenpf_efi_runtime_call`, `xenpf_firmware_info`, `xenpf_enter_acpi_sleep`, `xenpf_getidletime`, `xenpf_set_processor_pminfo`.
- Top-level `xen_platform_op` union with a 128-byte pad.

Integration notes: Includes `xen.h` and is intended for privileged domain-0 kernel/control code.

Risk/attention points: The union mixes many architecture- and firmware-specific layouts. ABI padding and interface version must be preserved exactly.
