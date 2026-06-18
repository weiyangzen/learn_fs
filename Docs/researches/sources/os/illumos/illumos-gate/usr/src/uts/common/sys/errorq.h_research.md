# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq.h

## Role

`errorq.h` defines the public kernel interface for the illumos error queue facility. Error queues collect fixed-size error records, optionally nvlist-backed, and drain them through callbacks, either asynchronously by soft interrupt or synchronously by the caller.

## Main Interfaces

- Forward-declares `errorq_t` and `errorq_elem_t`.
- Defines `errorq_func_t`, the callback type invoked to drain an element with private data, payload, and element metadata.
- Defines public create flag `ERRORQ_VITAL`, indicating the queue should be automatically drained on system reset.
- Defines dispatch modes `ERRORQ_ASYNC` and `ERRORQ_SYNC`.

## Kernel API

Under `_KERNEL`, the header declares:

- Creation/destruction: `errorq_create()`, `errorq_nvcreate()`, `errorq_destroy()`.
- Submission/drain: `errorq_dispatch()`, `errorq_drain()`, `errorq_init()`, `errorq_panic()`, `errorq_dump()`.
- Reservation path: `errorq_reserve()`, `errorq_commit()`, and `errorq_cancel()`.
- Nvlist element helpers: `errorq_elem_nvl()`, `errorq_elem_nva()`, and `errorq_elem_dup()`.
