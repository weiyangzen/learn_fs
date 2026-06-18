# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msreg.h

Software mouse event/register layout header.

Key responsibilities:
- Defines `struct mouseinfo` samples with signed x/y/wheel deltas, button bitmask, and 32-bit timeval timestamp.
- Defines hardware button bit positions for left/middle/right.
- Defines `struct mousebuf` circular buffer layout for mouse samples.
- Defines `struct ms_softc` state for the mouse buffer, event generation, read format, VUID address, and previous button state.
- Defines event-generation state constants for x/y movement, ten buttons, and wheel.
- Defines obsolete kernel `MSIOGETBUF` ioctl for exposing the mouse buffer pointer.

Dependencies:
- Includes `sys/types.h` and `sys/types32.h`; VUID constants are expected from surrounding input headers.

Notable risks:
- Some structures expose historical buffer layouts and 32-bit timestamps.
- The obsolete kernel ioctl exposes buffer internals and should remain compatibility-only.
