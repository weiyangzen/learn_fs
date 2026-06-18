# sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.h

Purpose: declares origin tracking structures and APIs.

Important APIs and data: `origin_data_t` embeds `avl_t` first, then `address`, `karma`, and `blocked`. Functions expose lifecycle, lookup, scoring, anomaly helpers, and IPv4 conversions.

Control flow: none in header; callers interact with global origin table in the implementation.

State and persistence: header exposes process-memory fields but no persistence.

Dependencies and integration: includes `avl.h` and `ids_config.h`; used by models, sessions, reactions, and timer services.

Risks: public struct fields allow direct mutation without preserving current-origin semantics. Address type documents an IPv4 hack and should not be assumed to support IPv6.

Test signals: integration tests should verify origin current pointer behavior after `find_origin`, `add_origin`, and scoring.
