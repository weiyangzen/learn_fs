# File Research: sources/virtualization/qemu/block/export/virtio-blk-handler.c

## Purpose
Shared virtio-blk request processor used by the VDUSE and vhost-user block export frontends. It translates virtqueue iovecs into QEMU `BlockBackend` coroutine operations.

## Request Validation
- Requires at least one output iovec for `virtio_blk_outhdr`.
- Requires at least one input iovec with space for trailing status byte.
- Strips the output header from the front of the output iovec list.
- Strips the status byte from the back of the input iovec list.
- Returns negative `-EINVAL` for structurally malformed requests.

## Range Checking
`virtio_blk_sect_range_ok()` enforces:
- Request size is 512-byte-sector aligned.
- Sector count is within `BDRV_REQUEST_MAX_SECTORS`.
- Byte offset is aligned to configured logical block size.
- Request range fits inside backend geometry from `blk_co_get_geometry()`.

## Supported Commands
- `VIRTIO_BLK_T_IN`: reads from backend into input iovecs.
- `VIRTIO_BLK_T_OUT`: writes output iovecs to backend if handler is writable.
- `VIRTIO_BLK_T_FLUSH`: calls `blk_co_flush()`.
- `VIRTIO_BLK_T_GET_ID`: copies handler serial into input iovecs, capped by `VIRTIO_BLK_ID_BYTES`.
- `VIRTIO_BLK_T_DISCARD`: validates one discard/write-zeroes descriptor, rejects unsupported flags, then calls `blk_co_pdiscard()`.
- `VIRTIO_BLK_T_WRITE_ZEROES`: validates descriptor and calls `blk_co_pwrite_zeroes()`, optionally with `BDRV_REQ_MAY_UNMAP`.
- Unknown commands return `VIRTIO_BLK_S_UNSUPP`.

## Status Handling
The function writes a virtio status byte into the request's final input buffer:
- `VIRTIO_BLK_S_OK` on success.
- `VIRTIO_BLK_S_IOERR` on backend/range/writable failures.
- `VIRTIO_BLK_S_UNSUPP` for unsupported commands or unsupported flags.

## Return Value
Returns the total input iovec length including the status byte so the transport frontend can push the used length back to the virtqueue.
