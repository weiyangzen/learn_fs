# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma.h

## Scope

Public client API for the InfiniBand Device Management Agent (IBDMA), used by protocol transports that provide I/O Controller profiles and services.

## APIs

- `ibdma_status_t` reports success, duplicate IOC GUID, full IOU, bad IOC profile, or bad parameter.
- `ibdma_hdl_t` is an opaque provider handle returned when an IOC registers.
- `ibdma_ioc_register()` registers an IOC GUID, IOC controller profile, and service entries, returning a handle.
- `ibdma_ioc_unregister()` removes a registered IOC.
- `ibdma_ioc_update()` updates a registered IOC profile and services.

## Behavior

- IBDMA manages an I/O Unit per IB HCA and responds to Device Management requests on all fabric ports.
- By default the IOUnit has no IOCs. Transport protocols register their IOCs and service entries, and IBDMA assigns IOUnit slots.
- Protocol transports call back into IBDMA as profile or service data changes.

## Dependencies

- Includes IBMF and IB Device Management attribute definitions.
- The profile and service records are IB DM wire/domain structures.

## Risks And Invariants

- IOC GUIDs must be unique; duplicates return `IBDMA_IOC_DUPLICATE`.
- The IOUnit has a finite slot count enforced by the implementation.
- Consumers must retain and use only valid `ibdma_hdl_t` handles returned from registration.
