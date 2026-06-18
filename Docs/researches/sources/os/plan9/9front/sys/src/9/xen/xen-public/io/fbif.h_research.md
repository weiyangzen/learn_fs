# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fbif.h

Imported Xen public virtual framebuffer protocol ABI.

Purpose:
- Defines the Xen virtual framebuffer shared page and in/out event formats.

Key content:
- Defines frontend-to-backend update and resize events.
- Defines backend-to-frontend refresh-period advice event.
- Defines fixed event sizes and shared-page ring offsets/macros.
- Defines `struct xenfb_page` with ring indexes, framebuffer dimensions, line length, memory length, depth, and framebuffer page directory.
- Defines default framebuffer dimensions under `__KERNEL__`.

Integration:
- Not used by the visible 9front Xen kernel drivers in the scan.
- Vendored for Xen public I/O protocol completeness.

Risks/notes:
- Shared-page layout and event sizes are fixed ABI.
- Uses `unsigned long` page directory entries, so ABI protocol selection matters across 32/64-bit peers.
