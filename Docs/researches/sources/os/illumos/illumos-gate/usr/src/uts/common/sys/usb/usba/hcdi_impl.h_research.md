# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi_impl.h

## Role

Defines private per-host-controller USBA state for HCDI instances.

## Key Interfaces

- `usba_hcdi_t` stores the HCD devinfo pointer, DMA attributes, HCD ops, flags, soft interrupt handle, callback queue, transfer/burst constraints, root hub `usba_device_t`, USB address allocation bitmap, logging handle, interrupt cookies, mutex, hotplug counters, device count, kstat handles, and default ugen binding mode.
- Declares `usba_hcdi_set_hcdi()` and `usba_hcdi_get_hcdi()` for associating HCDI state with a devinfo node.
- Declares subsystem lifecycle functions `usba_hcdi_initialization()` and `usba_hcdi_destroy()`.

## Design Notes

The USB address bitmap is protected by `hcdi_mutex`; several stable fields are explicitly marked readable without locks for framework access patterns.

## Risk Notes

This structure is shared between HCD registration, address assignment, callback processing, root-hub management, kstats, and ugen policy. Layout or locking mistakes can affect all devices under a controller.
