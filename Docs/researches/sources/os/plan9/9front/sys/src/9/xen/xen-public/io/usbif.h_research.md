# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/usbif.h

Imported Xen public USB frontend/backend protocol ABI.

Purpose:
- Defines Xen USB request/response rings for URB submission/unlink and connection notifications.

Key content:
- Defines USB spec version enum.
- Documents USB pipe bit layout for port number, unlink/submit flag, direction, device address, endpoint, and pipe type.
- Defines helpers for pipe port/unlink bits.
- Defines `USBIF_MAX_SEGMENTS_PER_REQUEST`.
- Defines `usbif_request_segment`, `usbif_urb_request`, `usbif_urb_response`, and URB ring type.
- Defines connection request/response structures and connection ring type.
- Defines ring-size constants using `__CONST_RING_SIZE`.

Integration:
- Not used by visible 9front Xen runtime code.
- Depends on `ring.h` and grant references.

Risks/notes:
- Requires `PAGE_SIZE` to be defined by the including environment for ring-size constants.
- Complex URB/ISO fields need host USB semantics to implement correctly.
