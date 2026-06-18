# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/nsap_addr.c

Implements NSAP address conversion helpers.

APIs:
- `inet_nsap_addr(ascii, binary, maxlen)`
- `inet_nsap_ntoa(binlen, binary, ascii)`

Behavior:
- `inet_nsap_addr` requires `0x`/`0X` prefix, ignores `.`, `+`, and `/`, parses hex pairs into binary, and returns byte length or `0` on failure.
- `inet_nsap_ntoa` emits `0x` followed by uppercase hex pairs, inserting dots after every two bytes; uses caller buffer or resolver thread-local `inet_nsap_ntoa_tmpbuf`.
- Caps output conversion at 255 input bytes.

Depends on `resolv_mt.h` for thread-specific fallback buffer.
