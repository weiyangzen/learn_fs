<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb_linux.h -->
# sources/test-tools/syzkaller/executor/common_usb_linux.h

## Purpose

`common_usb_linux.h` is the Linux raw-gadget transport implementation for syzkaller USB pseudo-syscalls. It wraps `/dev/raw-gadget` ioctls, connects generated virtual USB devices to dummy UDC instances, services endpoint-zero control requests, enables/disables raw endpoints for the current interface, and exposes endpoint read/write/control/disconnect pseudo-syscalls.

## Important APIs, Types, And Functions

Raw-gadget ABI definitions:

- `struct usb_raw_init`, `enum usb_raw_event_type`, `struct usb_raw_event`, `struct usb_raw_ep_io`, `struct usb_raw_ep_caps`, `struct usb_raw_ep_limits`, `struct usb_raw_ep_info`, and `struct usb_raw_eps_info` locally mirror the raw-gadget userspace ABI.
- `USB_RAW_IOCTL_*` macros define init, run, event fetch, EP0 read/write/stall, endpoint enable/disable/read/write, configure, vbus draw, and endpoint information ioctls.
- Thin wrappers include `usb_raw_open`, `usb_raw_init`, `usb_raw_run`, `usb_raw_configure`, `usb_raw_vbus_draw`, `usb_raw_ep0_write`, `usb_raw_ep0_read`, `usb_raw_event_fetch`, `usb_raw_ep_enable`, `usb_raw_ep_disable`, `usb_raw_ep0_stall`, `usb_raw_ep_write`, and `usb_raw_ep_read`.

Lookup and state helpers:

- `lookup_interface()` finds a parsed interface by interface number and alternate setting.
- `lookup_endpoint()` finds the raw-gadget handle for an endpoint address on the current interface.
- `USB_MAX_PACKET_SIZE` caps EP0 and endpoint transfer buffers at 4096 bytes.
- `struct usb_raw_control_event` and `struct usb_raw_ep_io_data` are fixed-size stack containers for raw events and I/O payloads.
- `set_interface()` disables endpoints from the previous interface, enables endpoints for the requested interface, stores returned endpoint handles into `usb_endpoint_index.handle`, and updates `iface_cur`.
- `configure_device()` draws configured bus power, issues raw-gadget configure, and activates interface 0.

Pseudo-syscalls:

- `syz_usb_connect_impl()` implements the shared connection loop for generic and ath9k USB connect.
- `syz_usb_connect()` passes the generic OUT request handler from `common_usb.h`.
- `syz_usb_connect_ath9k()` passes the ath9k-specific OUT request handler.
- `syz_usb_control_io()` handles one later EP0 control request using fuzzer-provided descriptor/response tables.
- `syz_usb_ep_write()` writes fuzzer data to a non-control endpoint by endpoint address.
- `syz_usb_ep_read()` reads from a non-control endpoint into fuzzer-provided memory.
- `syz_usb_disconnect()` closes the raw-gadget fd and sleeps briefly.

## Control Flow

`syz_usb_connect_impl()` is the central flow:

1. Validate and debug-dump the generated descriptor blob.
2. Open `/dev/raw-gadget`; reject fds above `MAX_FDS`.
3. Parse and publish descriptor indexes through `add_usb_index()`.
4. Initialize raw-gadget with speed, driver `"dummy_udc"`, and device name `dummy_udc.<procid>`.
5. Run the gadget.
6. Loop fetching raw-gadget events until the OUT handler marks connection done.
7. Ignore non-control events.
8. For IN control requests, resolve data through `lookup_connect_response_in()` or stall EP0.
9. For OUT control requests, call the selected OUT handler, optionally configure the device on SET_CONFIGURATION, then read the host payload.
10. Clamp response length to both the local 4096-byte buffer and `wLength`, perform EP0 read/write, and return the fd after a short sleep.

`syz_usb_control_io()` handles a single post-connect control event. It stalls unknown IN requests, handles SET_INTERFACE-like requests by switching active endpoint sets, fills or consumes EP0 data, and sleeps briefly before returning.

Endpoint read/write pseudo-syscalls translate a USB endpoint address to the raw endpoint handle cached by `set_interface()`, clamp length to 4096 bytes, perform the raw-gadget endpoint ioctl, and sleep.

## State And Persistence Behavior

This file mutates the generic USB index state from `common_usb.h`. `set_interface()` writes endpoint handles into the selected interface's endpoint indexes and updates `iface_cur`; `lookup_endpoint()` depends on that current-interface state.

The raw-gadget fd is returned to the generated program and also used as the key for `lookup_usb_index()`. Closing it via `syz_usb_disconnect()` does not remove the corresponding `usb_devices[]` slot. Because fd numbers may be reused, stale metadata can be a risk if a later raw-gadget connection reuses a closed fd while the table also contains older entries; lookup returns the first matching published fd.

The code introduces short `sleep_ms(200)` delays after connect/config/control/endpoint operations to let kernel-side USB state settle and to improve reproducibility.

## Dependencies And Integration Points

The implementation includes `common_usb.h` and depends on its descriptor parsing and response lookup functions. It expects Linux raw-gadget support at `/dev/raw-gadget`, dummy UDC devices named `dummy_udc.<procid>`, USB descriptor/request constants, `MAX_FDS` from the Linux executor header, and common executor symbols such as `procid`, `debug`, `debug_dump_data`, `sleep_ms`, and feature macros.

It is tightly coupled to syzlang layouts for `vusb_connect_descriptors`, `vusb_descriptors`, `vusb_responses`, endpoint pseudo-syscall signatures, and raw USB descriptor blobs.

## Risks And Edge Cases

- The raw-gadget ABI structs and ioctl numbers are copied locally. Kernel ABI changes require updating this header.
- `usb_raw_init()` uses `strncpy()` into fixed-size arrays without forcing a trailing NUL if input strings are too long. Current call sites use short constants.
- `syz_usb_connect_impl()` leaks the raw-gadget fd on some early failures after open/add/init/run errors because it returns without closing.
- `add_usb_index()` metadata remains after disconnect and failed cleanup, making fd reuse a possible stale-state hazard.
- EP0 response lengths above 4096 are converted to zero rather than truncated to 4096, while `wLength` is treated as the host-side cap.
- In `syz_usb_control_io()`, the condition for interface switching uses standard request type or `USB_REQ_SET_INTERFACE`; future class/vendor requests with the same request number may trigger interface lookup.
- Endpoint I/O requires a current interface. Before configuration or after failed interface setup, `lookup_endpoint()` returns `-1`.
- OUT request debug dumping in connect logs `event.data`, while the read payload is held in the response buffer; this may not show the actual just-read bytes.

## Test Signals

- Raw-gadget availability is indicated by successful open/init/run against `/dev/raw-gadget` and `dummy_udc.<procid>`.
- Connect tests should see EP0 request logs for GET_DESCRIPTOR, SET_CONFIGURATION, optional ath9k vendor requests, and final configured fd return.
- After SET_CONFIGURATION or SET_INTERFACE, endpoint enable/disable debug lines should show endpoint addresses and raw handles.
- Endpoint tests should verify `syz_usb_ep_write` and `syz_usb_ep_read` return success only for endpoints present in the current interface.
- Control I/O tests should cover unknown IN stall behavior, generated response lookup, OUT payload consumption, and interface switching by number/alternate setting.
- Disconnect should close the fd and allow raw-gadget event loops to unwind in executor close-fd cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb_linux.h -->
