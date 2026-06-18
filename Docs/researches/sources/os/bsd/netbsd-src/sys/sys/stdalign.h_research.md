# File Research: sources/os/bsd/netbsd-src/sys/sys/stdalign.h

Read completely: 55 lines.

This C/C++ compatibility header defines `alignas` and `alignof` for pre-C++11 modes by mapping them to `_Alignas` and `_Alignof`, and sets `__alignas_is_defined` and `__alignof_is_defined`.

Risks: no runtime behavior. It relies on compiler support for C alignment keywords when not in modern C++.
