# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/dst.h

ISC DNS Security Tool style crypto/key API header, with names remapped to private libc symbols.

Defines:
- `DST_KEY` structure unless already provided.
- Extensive `#define` namespace remaps from `dst_*` to `__dst_*`.
- Key operations for init, algorithm checks, signing, verification, reading/writing keys, DNS KEY conversion, buffer conversion, generation, freeing, comparison, and signature sizing.
- DNS key constants, algorithm codes, flags, and error codes.

Role: private imported resolver/DNSSEC support interface.
