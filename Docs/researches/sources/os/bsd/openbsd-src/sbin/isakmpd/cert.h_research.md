# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.h

This header defines the certificate handler abstraction for `isakmpd`.

Key contents:
- `struct cert_handler`: a vtable for certificate operations including init, CRL init, parse, validate, insert, free, certificate-request handling, obtain, key extraction, subject extraction, duplication, serialization, printable conversion, and CA counting.
- `struct certreq_aca`: stores decoded acceptable certificate authority data, raw CA bytes, handler pointer, and list linkage.
- Prototypes for certificate request decoding, subject freeing, handler lookup, certificate initialization, and CRL initialization.

Dependencies:
- Uses `TAILQ_ENTRY` from `<sys/queue.h>`.

Research notes:
- This header is a core extension point for supported certificate encodings in IKE authentication.
