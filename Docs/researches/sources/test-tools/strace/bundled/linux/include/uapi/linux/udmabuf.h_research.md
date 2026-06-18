# sources/test-tools/strace/bundled/linux/include/uapi/linux/udmabuf.h

## Purpose

Defines the ioctl ABI for creating userspace DMA-BUF objects from memfd-backed memory. strace uses it to decode `/dev/udmabuf` creation requests.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `linux/ioctl.h`. It exports `UDMABUF_FLAGS_CLOEXEC`, `struct udmabuf_create` for a single memfd/offset/size, `struct udmabuf_create_item` for list elements, `struct udmabuf_create_list` with flags, count, and flexible `list[]`, and ioctl numbers `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST`.

## Control Flow, State, and Integration

Runtime flow is ioctl based: userspace passes one or more memfd ranges and receives a DMA-BUF fd from the kernel driver. State is fd-scoped: source memfds, exported DMA-BUF objects, offsets, sizes, and close-on-exec behavior.

## Risks and Test Signals

Risks include incorrect flexible-array sizing for list creates, integer overflow in count-to-byte calculations, invalid offset/size alignment assumptions, and missing close-on-exec flag decode. Test signals include ioctl decode for single and list create requests, list item iteration by `count`, and named flag display.
