# File Research: sources/os/bsd/netbsd-src/sys/sys/kcov.h

Defines the KCOV kernel coverage interface and ioctl ABI. It includes commands for buffer sizing, enable/disable, remote attach/detach, remote VHCI identifiers, coverage modes, and coverage entry type. Kernel prototypes are compiled when `KCOV` is enabled; otherwise macros collapse to `__nothing`.

This header supports fuzzing/instrumentation paths. Risks include exposing coverage only when correctly configured, matching buffer entry size with userland tooling, and avoiding coverage recursion through silence enter/leave.
