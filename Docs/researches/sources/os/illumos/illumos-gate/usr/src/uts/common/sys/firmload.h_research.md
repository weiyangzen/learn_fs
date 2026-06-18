# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/firmload.h

Defines a small kernel-only firmware loading API derived from NetBSD. It introduces opaque `firmware_handle_t` and declares `firmware_open`, `firmware_close`, `firmware_get_size`, and `firmware_read`.

The API is only visible under `_KERNEL` and includes `sys/types.h`. Callers open firmware by name/path components, query size, read at offsets into caller buffers, then close the handle.

This is an abstraction header for drivers that load firmware blobs without directly depending on filesystem details.
