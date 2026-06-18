# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.h

`vendor.h` defines `struct vendor_cap`, holding a vendor text string plus computed hash and hash size. It declares the OpenBSD vendor-ID initialization, outgoing payload addition, and incoming payload check functions.

The header connects vendor handling with the message and payload structures from the exchange layer.
