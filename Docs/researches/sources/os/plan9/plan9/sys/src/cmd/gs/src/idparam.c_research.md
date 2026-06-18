# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.c

Implements typed dictionary parameter extraction helpers.

Supported parameter forms:
- booleans
- signed/unsigned integers, including null-aware signed ints
- floats
- integer arrays, fixed-size integer arrays
- float arrays with optional defaults
- procedures with invalid/empty defaults
- matrices
- UniqueID/XUID
- UID equality checks

Notable compatibility choices:
- Integral reals are accepted for integer parameters and integer arrays because some Fontographer output violates Adobe specs.
- `dict_uid_param` prefers XUID in Level 2, allocates XUID storage, treats UniqueID 0 as invalid/no UID, and validates UniqueID range `0..0xffffff`.
