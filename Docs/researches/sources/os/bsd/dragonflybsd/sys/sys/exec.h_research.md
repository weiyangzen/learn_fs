# File Research: sources/os/bsd/dragonflybsd/sys/sys/exec.h

`exec.h` defines common exec-related structures. Publicly it defines `struct ps_strings`, the user-stack metadata used by tools such as `ps` to find argv and environment strings, plus `PS_STRINGS` and `SPARE_USRSPACE`.

It declares `struct execsw`, the executable image activator switch with an image-activation function and name. It includes `machine/exec.h` for machine-specific exec definitions.

Under `_KERNEL`, it declares page-mapping helpers for exec image inspection, exec switch registration/unregistration, and macros to define executable image modules through the module subsystem.
