# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_set.c

Implements in-place updates of existing encoded SDP elements.

Key behavior:
- `sdp_set_bool` rewrites a boolean payload when the element tag matches.
- `sdp_set_uint` and `sdp_set_int` rewrite values only if the existing element width can hold the new value.
- 128-bit integer setters write a sign/zero high half and the value low half.
- `_sdp_set_ext` updates sequence/alternative length fields for existing EXT8/EXT16/EXT32 elements.
- `sdp_set_seq` and `sdp_set_alt` are thin wrappers over `_sdp_set_ext`.

Dependencies:
- Public SDP tag macros and endian encoders.

Notes:
- The file does not provide string or URL setters; callers must write those payloads separately after length management.
