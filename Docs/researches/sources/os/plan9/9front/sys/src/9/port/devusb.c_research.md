# File Research: sources/os/plan9/9front/sys/src/9/port/devusb.c

Implements the Plan 9 USB device framework at `#u`. It does not enumerate devices itself; user-space `usbd` drives enumeration using this kernel endpoint abstraction. Host-controller implementations register via `addhcitype`.

The namespace contains `usb/ctl` and endpoint directories `epN.M` with `data` and `ctl`. Endpoint zero represents a USB device; additional endpoints are created with control commands. `newdev` creates device endpoint zero, tracks hub/root-port/topology state, handles transaction translator metadata, and assigns device ids. `newdevep` creates nonzero endpoints with default transfer parameters.

Control commands cover new endpoint/device creation, detach, reset, debug, clear halt, address assignment, hub configuration, max packet size, transfer descriptors, poll interval, timeout, isochronous timing, endpoint names, and info strings. Root hubs are faked with `rhubread`/`rhubwrite`, translating hub class requests into HCI port operations.

`usbopen` validates endpoint type/mode, enforces exclusive data opens, computes bandwidth/load, and calls HCI endpoint open. `usbread`/`usbwrite` dispatch endpoint I/O through HCI hooks, with special root-hub handling. Locking and refcounts around `eps[]`, `Ep`, and `Udev` are central to safe endpoint lifetime.
