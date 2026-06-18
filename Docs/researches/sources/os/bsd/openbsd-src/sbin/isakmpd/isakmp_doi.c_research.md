# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.c

Minimal ISAKMP DOI registration and handlers.

This DOI is mostly a compatibility shell around informational exchanges. It registers a DOI with no DOI-specific state sizes, no SPI allocation/deletion hooks, no exchange script, no situation bytes, and IPsec ID decoding for reporting.

Validation is intentionally narrow: DOI data in ID payloads must be zero, key information is accepted without work, situations are empty, and most attribute/protocol/transform/exchange validation paths reject if reached. Initiator support only sends informational messages; responder support handles informational NOTIFY payloads, dispatches DPD notifications, marks other notifications and DELETEs handled, and rejects SA proposals with no-proposal-chosen.
