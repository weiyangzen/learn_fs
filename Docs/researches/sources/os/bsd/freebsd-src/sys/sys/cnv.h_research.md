# File Research: sources/os/bsd/freebsd-src/sys/sys/cnv.h

## Purpose
Declares cookie-based nvlist accessors for inspecting, retrieving, taking, and freeing name/value pairs without re-looking them up by name.

## Main Elements
- Metadata helpers: `cnvlist_name()` and `cnvlist_type()`.
- Get APIs for bool, number, string, nvlist, binary, and arrays.
- Userland-only descriptor accessors are included outside `_KERNEL`.
- Take APIs remove the item and transfer ownership to the caller.
- Free APIs remove and free the item identified by a cookie.

## Dependencies And Integration
Uses `sys/_nv.h`; outside the kernel it includes standard bool/int/stdarg/stdio headers and `sys/nv_namespace.h`.

## Risk Notes
Pointer-returning get APIs expose internal storage that must not be freed by the caller. Take APIs transfer ownership and require matching cleanup.
