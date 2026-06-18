# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/physmem.h

## Purpose
Defines ioctl command numbers and argument structures for a physical-memory mapping/allocation interface.

## Main Interfaces
- Ioctls:
  - `PHYSMEM_SETUP`
  - `PHYSMEM_MAP`
  - `PHYSMEM_DESTROY`
- Mapping flags:
  - `PHYSMEM_CAGE`
  - `PHYSMEM_RETIRED`
- `struct physmem_setup_param`: requested physical address, length, user VA, and returned destroy cookie.
- `struct physmem_map_param`: requested physical address, returned VA, and flags.

## Dependencies And Relationships
Uses fixed-width integer types. Consumers pass these structures through the corresponding driver ioctl interface.

## Research Notes
The interface distinguishes setup/destroy lifecycle from mapping. Flags allow callers to request caged or retired-page behavior.
