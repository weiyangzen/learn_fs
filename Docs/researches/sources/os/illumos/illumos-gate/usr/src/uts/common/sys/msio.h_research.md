# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msio.h

Mouse ioctl ABI header.

Key responsibilities:
- Defines `Ms_parms` for mouse jitter threshold, speed law, and speed limit.
- Defines `Ms_screen_resolution` for screen height and width.
- Defines mouse ioctl command base and commands to get/set parameters, query button count, and set screen resolution.

Dependencies:
- Standalone public header guarded for C++.

Notable risks:
- Ioctl numeric values share the `'m' << 8` base with tape comments noting overlap; consumers rely on stable command numbers.
