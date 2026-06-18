# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icsmap.h

Interface for loading cached color-space maps for Indexed or substituted Separation spaces.

Defines execution-stack layout constants for map loading and declares:
- `zcs_begin_map(...)`

The note clarifies that the underlying color space is a direct space, not just a base space, because Indexed spaces may map into Separation or DeviceN spaces.
