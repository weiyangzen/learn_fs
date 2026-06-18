# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmp.h

Read completely: 68 lines.

This header defines `struct utmp50`, the old utmp record format with `int32_t ut_time`, and inline converters between `struct utmp` and `struct utmp50`. It declares compatibility `getutent` and current `__getutent50` symbols.

Important interactions: conversion is mostly raw `memcpy` with only the time field adjusted. It depends on the beginning layout of current `struct utmp` remaining compatible with the old fixed-size fields.

Security/reliability notes: no direct runtime logic beyond inline conversion. The 32-bit timestamp conversion can truncate modern timestamps.
