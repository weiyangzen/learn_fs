# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fsdir.c

Multiplexing root directory for multiple USB driver file systems.

Main behavior:
- Maintains a dynamically resized array of registered `Usbfs*`.
- `usbfsadd` assigns a high-32-bit qid namespace and registers a subtree.
- `usbfsdel` and `usbfsgone` unregister subtrees, call end hooks, close devices, and optionally exit when all are gone.
- `usbfsdirdump` prints registered filesystem state.
- Root `fswalk`, `fsopen`, `fsread`, `fswrite`, `fsclunk`, and `fsstat` dispatch operations to the correct registered filesystem based on qid high bits.
- `usbdirfs` is the exported root `Usbfs` used by USB drivers and `usbd`.

Design:
- qid high 32 bits identify the registered device/subtree; low bits are private to that subtree.
- Operations take temporary references on underlying `Dev` objects while dispatching.
- Entry 0 is reserved for the top-level root.

This file lets independent USB drivers appear under one mounted `/dev` or `/net` directory.
