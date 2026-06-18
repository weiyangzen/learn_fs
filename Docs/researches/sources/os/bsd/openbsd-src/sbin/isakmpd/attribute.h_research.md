# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.h

This header declares ISAKMP attribute helper functions.

Key contents:
- Forward declaration of `struct constant_map`.
- Prototypes for:
  - `attribute_map`
  - `attribute_set_basic`
  - `attribute_set_constant`
  - `attribute_set_var`

Research notes:
- This is a compact shared interface for modules that encode or validate ISAKMP transform attributes.
