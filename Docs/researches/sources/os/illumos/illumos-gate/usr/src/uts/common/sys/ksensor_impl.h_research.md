# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksensor_impl.h

## Purpose
Defines implementation glue for the kernel sensor subsystem.

## Main Interfaces
- `ksensor_init()`: initializes the subsystem.
- Operation vectors:
  - `ksensor_op_kind()`
  - `ksensor_op_scalar()`
- Callback types:
  - `ksensor_create_f`
  - `ksensor_remove_f`
- Registration APIs:
  - `ksensor_register()`
  - `ksensor_unregister()`

## Dependencies And Relationships
Includes `sys/sensors.h` for public sensor ioctl structures and device types. Registration is keyed by `dev_info_t *`.

## Research Notes
This is a small internal header connecting sensor providers to central ksensor device operations. It separates provider registration callbacks from ioctl operation handlers.
