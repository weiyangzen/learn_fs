# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icsmap.h

Declares shared cached color-space map loading support.

Key points:
- Defines execution-stack frame layout for cached map loading: component count, map object, procedure, hival, and index.
- Declares `zcs_begin_map`, which sets up loading for Indexed or substituted Separation color spaces.
- Accepts an indexed map output pointer, mapping procedure, entry count, direct base color space, and continuation procedure.

Research notes:
- The base parameter is a direct color space because Indexed base spaces may themselves be Separation or DeviceN.
