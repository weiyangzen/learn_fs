# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_impl.h

## Role

Central private USBA implementation header tying together HCDI, hubdi, request wrappers, logging, enumeration, BOS handling, hotplug stats, and pipe/device utility functions.

## Key Interfaces

- Defines ugen binding modes for HCD `.conf` files and USB address allocation limits.
- `usba_pipe_async_req_t` describes asynchronous pipe management calls with callback and synchronous worker function.
- `usba_pm_req_t` describes asynchronous/nonblocking PM power-change requests.
- `usba_req_wrapper_t` is the private allocation wrapper around control/bulk/interrupt/isoc requests. It provides callback queue links, allocated-request tracking, synchronous completion CV, request owner, HCD private data, pipe pointer, completion reason, callback flags, request attributes, and allocation length.
- Provides macros converting between wrapper, request, request queues, allocated queues, and per-request pipe data.
- Declares HCD private accessors for control requests and USB address set/unset helpers.
- Defines private `usba_hubdi_t` and declares major subsystem init/destroy functions.
- Declares allocation/free, pipe state, async setup, callback drain, default pipe, pipe handle refcount, persistent pipe, leak checking, child device creation/destruction, BOS retrieval/property/free, hotplug stats, callback dispatch, and logging helpers.
- Defines debug print masks and `usba_log_handle_impl_t`.
- Defines node-name matching entries and node kind flags for device/interface/interface-association naming.
- Defines `usb_dev_cap_t` for USB device capture callback registration.

## Design Notes

The wrapper layout intentionally allocates USBA metadata immediately before the public request structure. Macros use pointer arithmetic to move between them.

## Risk Notes

Request wrapper pointer arithmetic, per-pipe task queues, callback queues, and sync CVs are core transfer machinery. Any mismatch in allocation layout or callback state handling can corrupt requests, leak allocations, or deadlock synchronous transfers.
