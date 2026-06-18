# File Research: sources/os/bsd/dragonflybsd/sys/kern/cpu_if.m

## Summary
Defines a minimal `cpu` kernel object interface.

## Main Contents
- Includes bus and sensor headers.
- Declares `INTERFACE cpu`.
- Defines one method, `get_sensdev`, returning a `struct ksensordev *` for a CPU device.

## Risks
The interface has no default implementation. Drivers or CPU bus glue calling `CPU_GET_SENSDEV` need a concrete method or must handle absent method behavior from the generated interface layer.
