# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/kexec.h

Imported Xen public kexec/kdump hypercall ABI.

Purpose:
- Defines Xen’s public kexec operation interface for dom0 reboot/crash-kernel loading and crash range discovery.

Key content:
- Documents three operation groups: range information, load/unload images, and executing a loaded image.
- Defines `KEXEC_XEN_NO_PAGES` for x86.
- Defines kexec types default and crash.
- Defines `xen_kexec_image_t` with page list, indirection page, and start address.
- Defines command IDs and structures for execute, load/unload, and get-range.
- Defines range IDs for crash area, Xen, CPU notes, xenheap, obsolete ia64 boot param, EFI memory map, and vmcoreinfo.

Integration:
- Dom0/control-plane ABI; not used by 9front’s guest block/network runtime.

Risks/notes:
- Machine-address ranges and crash-kernel paths are host/control-stack sensitive.
- x86 page-list count is fixed by ABI.
