# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kd.h

## Role

`kd.h` provides minimal compatibility definitions for historical `kd` display-mode ioctls. The file explicitly warns it may be deleted or changed without notice.

## Major Definitions

The ioctl namespace is `KDIOC` as `('K' << 8)`. `KDGETMODE` and `KDSETMODE` query and set text/graphics mode. Mode values are `KD_TEXT`, `KD_GRAPHICS`, and `KD_RESETTEXT`.

## Interfaces

There are no functions or structures. The header only exports compatibility ioctl constants.

## Integration Notes

This is a narrow compatibility shim. Any code using it should treat the interface as legacy and avoid extending it unless required for old consumers.
