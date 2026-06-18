# File Research: sources/os/plan9/9front/sys/src/9/xen/dat.h

Xen-specific kernel data compatibility header.

Purpose:
- Extends the PC kernel data definitions with Xen ABI types, globals, and mapping helpers.

Key content:
- Includes `../pc/dat.h`.
- Defines fixed-width integer aliases and Plan 9-local errno constants expected by imported Xen headers.
- Includes `xendat.h` and normalizes `mk_unsigned_long` and guest-handle macros.
- Declares `hypervisor_virt_start`, `patomfn`, `matopfn`, `xenstart`, `xentop`, and `HYPERVISOR_shared_info`.
- Replaces normal `kmap`/`kunmap` with simple direct `KZERO`-based mappings.

Integration:
- Required by Xen MMU, console, storage, network, xenstore, and hypercall code.

Risks/notes:
- The “fake kmap” is explicitly questioned in comments and relies on Xen’s direct mapping model for this port.
