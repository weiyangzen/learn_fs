# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_buf.h

Private buffer-allocation interface for IEEE 1394 OpenHCI adapter DMA-bound memory. It describes caller parameters, returned DMA/access handles, and the opaque handle used to free allocated buffers.

Key elements:
- `hci1394_buf_parms_t` describes requested buffer length, maximum DMA cookie count, and alignment. The cookie/alignment fields override adapter default DMA attributes for scatter-gather length and alignment.
- `hci1394_buf_info_t` returns the DMA cookie, cookie count, kernel virtual address, requested and real allocation lengths, access handle, and DMA handle.
- `hci1394_buf_t` privately tracks access handle, DMA handle, and driver info pointer.
- `hci1394_buf_handle_t` is the opaque allocation handle passed to `hci1394_buf_free()`.
- Declares `hci1394_buf_attr_get()` for default DMA attributes.
- Declares `hci1394_buf_alloc()` and `hci1394_buf_free()` for allocation lifecycle.
- Warlock annotation marks the buffer structures as single-user protected.

Dependencies:
- Depends on illumos DDI DMA/access-handle types and adapter driver info type.
- Intended consumers are queue, descriptor, async, and isochronous code needing memory mapped for device DMA.

Research notes:
- The API separates allocation metadata returned to the caller from the opaque free handle, allowing clients to use cookies/addresses while the module retains enough private state to unbind/free correctly.
