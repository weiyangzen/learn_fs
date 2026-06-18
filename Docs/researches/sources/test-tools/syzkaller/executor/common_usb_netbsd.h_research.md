# sources/test-tools/syzkaller/executor/common_usb_netbsd.h

Purpose: NetBSD-specific implementation of syzkaller USB pseudo-syscalls. It adapts the Linux-oriented `common_usb.h` descriptor model to NetBSD VHCI device APIs so generated programs can attach and enumerate virtual USB devices.

Important APIs and types: the file redefines packed Linux-style USB descriptor structs and request constants, then exposes `vhci_open`, `vhci_setport`, `vhci_usb_attach`, `vhci_usb_recv`, `vhci_usb_send`, `syz_usb_connect_impl`, `syz_usb_connect`, and `syz_usb_disconnect`. `syz_usb_connect_impl` is the main control-flow hub: it builds a USB descriptor index with `add_usb_index`, selects port 1, attaches the device, receives VHCI control requests, resolves IN/OUT responses through `lookup_connect_response_in` or the supplied OUT resolver, and sends or receives endpoint-zero payloads until configuration completes.

State and dependencies: state is held in the VHCI file descriptor, the global `procid` path `/dev/vhci%llu`, and descriptor indexes owned by `common_usb.h`. The code depends on NetBSD headers, `ioctl` command contracts, `debug`, `debug_dump_data`, and `sleep_ms`.

Integration points: compiled when the executor or csource needs `syz_usb_connect`/`disconnect`; NetBSD coverage can attach remote VHCI coverage in `executor_bsd.h`.

Risks and tests: short reads/writes are looped, but `vhci_usb_recv` treats EOF as a zero-length progress bug that can spin if `read` returns 0 before completion. Control request behavior is strict and returns `-1` for unknown requests, making descriptor lookup correctness critical. Test coverage is indirect through USB feature setup and executor runtime; no dedicated NetBSD unit test appears in this subset.
