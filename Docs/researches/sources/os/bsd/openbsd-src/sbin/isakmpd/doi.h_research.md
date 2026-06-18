# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.h

This header defines the DOI handler interface for `isakmpd`.

Key contents:
- Forward declarations for exchange, message, payload, protocol, SA, and keystate structures.
- `struct doi`: a large vtable for DOI-specific behavior, including:
  - object size declarations for exchange/SA/proto data
  - attribute debugging, validation, and incompatibility checks
  - SPI deletion and extraction
  - exchange script selection
  - exchange finalization and cleanup
  - keystate lookup
  - leftover payload handling
  - informational pre/post hooks
  - protocol initialization
  - situation setup/validation
  - SPI size, protocol, transform, notification, ID, and key validation
  - initiator/responder handlers
  - ID decoding for reports/debugging
- Registry API prototypes:
  - `doi_init`
  - `doi_lookup`
  - `doi_register`

Research notes:
- This is the abstraction boundary between generic ISAKMP exchange machinery and IPsec DOI-specific policy/proposal semantics.
