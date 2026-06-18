# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi_impl.h

## Role

Small private lofi implementation header for nvlist-backed custom data/cache state.

## Structure

Includes `sys/nvpair.h`, defines `lofi_nvl_t` with mutex, condition variable, and `nvlist_t *`, and declares global `lofi_devlink_cache`.

## Dependencies And Consumers

Consumed by lofi implementation files that maintain device-link/custom data in an nvlist. It relies on kernel synchronization types being visible in the build context.

## Important Details

The structure is explicitly private implementation detail. Synchronization ownership is in the driver; the header only provides storage layout.

## Research Notes

Read completely: 41 lines, 884 bytes.
