# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/kbdif.h

Imported Xen public virtual keyboard/mouse protocol ABI.

Purpose:
- Defines shared-page event formats for Xen virtual keyboard and pointer input.

Key content:
- Defines backend-to-frontend event types for motion, key, and absolute position.
- Defines `xenkbd_motion`, `xenkbd_key`, and `xenkbd_position`.
- Defines fixed in/out event sizes, ring sizes, offsets, and ring access macros.
- Defines `struct xenkbd_page` with in/out consumer/producer indexes.

Integration:
- Not used by visible 9front Xen kernel drivers in this subset.
- Vendored for Xen public I/O protocol completeness.

Risks/notes:
- Keycodes reference Linux input key definitions, which may not map directly to Plan 9 without translation.
