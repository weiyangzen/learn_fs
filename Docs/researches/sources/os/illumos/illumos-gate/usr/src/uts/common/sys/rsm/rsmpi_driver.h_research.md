# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi_driver.h

## Role

`rsmpi_driver.h` defines the registration interface used by RSMPI controller drivers to register with the RSMOPS module.

## Structures

`rsmops_registry_t` contains:
- RSMPI driver version.
- driver name with `MAX_DRVNAME` 15 plus terminator.
- get-controller handler.
- release-controller handler.
- driver thread entry point.

`rsmops_ctrl_t` records one registered controller: number, outstanding-handle refcount, attributes, provider handle, next pointer, and back pointer to its driver registry.

`rsmops_drv_t` records one registered driver: registry data, controller count, driver list link, controller list head, and thread ID.

## APIs

The header declares:
- `rsm_register_controller()`
- `rsm_unregister_controller()`
- `rsm_register_driver()`
- `rsm_unregister_driver()`

## Research Notes

This is the provider registration companion to `rsmpi.h`. Driver/controller lifetime and outstanding controller-handle refcounts are the main correctness concerns.
