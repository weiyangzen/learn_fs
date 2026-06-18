# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/util.h

`util.h` declares the shared utility API for `isakmpd`. It exposes byte-order helpers, hex conversion, sockaddr conversion/accessors, port parsing, address formatting, zero tests, secret-file checks, timeout math, string expansion, and the `allow_name_lookups` flag.

It also declares the platform hook `sysdep_cleartext()`, used by UDP transports to keep IKE control traffic out of IPsec processing.

Because many daemon modules include this header, API changes here have broad impact across transport, config, crypto/cert, UI, and message code.
