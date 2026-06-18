# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_ntoa.c

Read completely: 110 lines.

This implements legacy `ns_ntoa`, formatting an NS address into a static buffer. It prints the network in hex, appends host bytes with leading zero compression, appends a port if present, and uses `spectHex` to uppercase hex letters and append `H` when needed to disambiguate numeric-looking hex strings.

Important interactions: returns a pointer to a static 40-byte buffer, matching old libc behavior but not thread-safe.

Security/reliability notes: uses `sprintf` into fixed buffers, but field sizes are bounded by NS address widths. Static result storage means concurrent calls can overwrite previous results.
