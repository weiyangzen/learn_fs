# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/s1394_impl.h

This small shared header defines framework-wide implementation typedefs.

Key content:
- Defines `_OPAQUE_T` and `typedef void *opaque_t` if it has not already been defined.

It is included by public and private 1394 headers that expose callback arguments or private opaque values. No functions, structures beyond the typedef, or constants are present.
