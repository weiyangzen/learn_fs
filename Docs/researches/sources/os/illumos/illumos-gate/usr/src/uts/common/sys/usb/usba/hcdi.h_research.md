# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi.h

## Role

Defines the Host Controller Driver Interface (HCDI): the operations vector and support routines used by USBA to call USB host controller drivers.

## Key Interfaces

- `usba_hcdi_ops_t` is the HCD operation vector registered at attach time. It includes PM support, pipe open/close/reset, data-toggle reset, control/bulk/interrupt/isochronous transfers, polling stop, frame-number queries, max isochronous packet queries, console input/output hooks, device initialization/finalization/addressing, and hub update support.
- Defines versioned HCD ops constants through `HCDI_OPS_VERSION_2`.
- `usba_hcdi_cb()` routes HCD transfer completion into synchronous waiters or asynchronous normal/exception callbacks.
- Provides request duplication helpers for interrupt and isochronous requests.
- Provides accessors for request private data, pipe data, endpoint data toggle state, and HCD device private storage.
- Provides allocation/registration/unregistration APIs for HCDI ops via `usba_alloc_hcdi_ops`, `usba_hcdi_register`, and `usba_hcdi_unregister`.
- Defines HCDI hotplug and error kstat structures and macros to access their kstat data.
- Defines `HCDI_DEFAULT_TIMEOUT` for non-periodic transfers when clients do not specify a timeout.

## Design Notes

This is the main contract boundary between framework code and controller-specific drivers. The operation vector is versioned so USBA can support old and new host-controller implementations.

## Risk Notes

Callback behavior depends on `USB_FLAGS_SLEEP`, completion reason, and request wrapper state. Incorrect HCD callback or ops-version handling can break synchronous waits, async callback ordering, transfer error reporting, or polled console support.
