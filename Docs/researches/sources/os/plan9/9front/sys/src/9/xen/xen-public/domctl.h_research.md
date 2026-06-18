# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/domctl.h

Imported Xen public domain-control ABI for node control tools.

Purpose:
- Defines the `domctl` hypercall command payloads used by Xen tools/control stacks for domain lifecycle, memory, vCPU, scheduler, device assignment, HVM state, memory events, sharing, debugging, and affinity.

Key content:
- Tools-only guard: errors unless compiling Xen or Xen tools.
- Defines `XEN_DOMCTL_INTERFACE_VERSION`.
- Provides domain creation and information structures, including HVM/HAP/S3/OOS flags and domain state flags.
- Defines memory list/page-frame info operations and page type/status constants.
- Defines shadow paging operations, dirty bitmap handling, and shadow memory allocation controls.
- Defines vCPU context/info, CPU/node affinity, scheduler parameters, domain handle/debugging, IRQ/I/O memory/I/O port permissions.
- Defines HVM context get/set/partial, address-size, real-mode area, triggers, PCI/device assignment, pass-through IRQs, memory and I/O port mappings.
- Defines CPUID, extended vCPU context/state, TSC info, mem-event, mem-sharing, audit, broken-page, and gdbsx debug structures.
- Ends with the main `struct xen_domctl` command union and command-number table.

Integration:
- Not compiled into normal 9front guest code because it is a control-tool interface.
- Other vendored Xen public headers, such as `sysctl.h`, depend on its types.
- Useful context for understanding the complete Xen ABI snapshot bundled under `xen-public`.

Risks/notes:
- Large, packed public control ABI with many version-sensitive fields.
- Includes HVM save-state and grant-table types; changes can ripple through tool builds.
- Not a filesystem/block path directly, except through domain/device/memory control semantics.
