# File Research: sources/os/bsd/netbsd-src/sys/sys/inttypes.h

Small public compatibility header for C99 integer format conversion macros. It includes `sys/stdint.h` and conditionally includes `machine/int_fmtio.h` for non-C++ consumers, C++ consumers opting into `__STDC_FORMAT_MACROS`, or C++11 and later.

It contains no runtime code. Its main role is ABI/source compatibility for fixed-width integer printing/scanning macros, with the important behavior gated by language mode and feature macros.
