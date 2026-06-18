# File Research: sources/os/bsd/netbsd-src/lib/libc/net/linkaddr.c

Link-layer address text conversion helpers. `link_addr()` parses an optional interface-name prefix followed by delimited hexadecimal bytes into a caller-provided `sockaddr_dl`, setting `AF_LINK`, `sdl_nlen`, `sdl_alen`, and possibly extending `sdl_len`.

`link_ntoa()` formats a `sockaddr_dl` into static storage, preserving the optional interface-name prefix and rendering address bytes as dot-separated lowercase hex. It bounds output through the `ADDC` macro and forces the last byte of the static buffer to NUL before formatting.
