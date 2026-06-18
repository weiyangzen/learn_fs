# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.c

This file provides certificate handler dispatch for `isakmpd`.

Key responsibilities:
- Registers built-in certificate handlers for X.509 signatures and KeyNote.
- Initializes certificate and CRL subsystems.
- Looks up handlers by ISAKMP certificate encoding ID.
- Decodes certificate request acceptable-authority payloads.
- Frees arrays of certificate subject buffers.

Important data and functions:
- `cert_handler[]`: table of X.509 and KeyNote handler vtables.
- `cert_init()`: runs available `cert_init` callbacks.
- `crl_init()`: runs available `crl_init` callbacks.
- `cert_get()`: finds a handler by encoding ID.
- `certreq_decode()`: validates handler availability, decodes authority data, preserves raw CA bytes, and returns `struct certreq_aca`.
- `cert_free_subjects()`: frees subject ID/length arrays.

Dependencies:
- X.509 support via `x509.h`.
- KeyNote certificate support via `policy.h`.
- ISAKMP certificate encoding constants from `isakmp_num.h`.

Research notes:
- The handler table abstracts certificate storage, validation, serialization, printable conversion, and key extraction across certificate formats.
