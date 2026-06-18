# File Research: sources/os/plan9/9front/sys/src/9/xen/mem.h

Xen x86 memory and address-space constants.

Purpose:
- Defines sizes, kernel/user virtual layout, Xen shared fixed mappings, segment selectors, and x86 PTE macros.

Key definitions:
- 4 KiB pages, 4 KiB kernel stack, up to 8 virtual CPUs.
- Kernel space starts at `KZERO=0x80000000`; user space is below that.
- Fixed Xen-related virtual addresses include `XENCONSOLE`, `XENSHARED`, `XENBUS`, and `XENGRANTTAB`.
- Segment selector aliases map to Xen-provided flat ring 1/ring 3 selectors.
- Defines PTE flags and index macros that switch between non-PAE and PAE behavior using `paemode`.

Integration:
- Used by Xen C and assembly for MMU, trap, console, and hypercall setup.

Risks/notes:
- PAE-aware macros rely on `paemode` global runtime state.
- Kernel/user split constrains usable memory mapping in `main.c`.
