# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba10.h

## Role

Declares legacy USBA 1.0 wrapper entry points and compatibility functions exported to older USB client drivers.

## Key Interfaces

- Exposes internal helpers needed by the `usba10_calls` module, including descriptor endpoint lookup, endpoint number, clear-feature, bulk transfer-size, max isochronous packet count, PM-enabled query, descriptor-tree logging, client registration, and log-handle allocation.
- Declares `usba10_` wrappers for client register/unregister, descriptor tree free/print/log, data parsing, endpoint lookup, string descriptor retrieval, address/interface queries, device ownership, and pipe state/open/close/drain/reset/private-data operations.
- Declares wrapper allocation/free and transfer calls for control, bulk, interrupt, and isochronous requests.
- Declares wrapper calls for configuration, alternate interface, feature/status, current frame, maximum isochronous packets, power changes, remote wakeup, PM component creation, device power-level no-ops, async requests, event callbacks, checkpoint failure, logging, same-device checks, status-string helpers, rval-to-errno, and serialization helpers.

## Design Notes

This file preserves old driver source/binary expectations by forwarding legacy API names to newer USBA functionality.

## Risk Notes

Compatibility wrappers must keep old semantics while calling newer internals. Subtle differences in blocking, callback, PM, or request allocation behavior can break legacy USB drivers.
