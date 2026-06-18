# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.h

This header defines the generic constant-map structure and lookup API.

Key contents:
- `struct constant_map` with `value`, `name`, and optional linked map pointer.
- Prototypes for:
  - `constant_link_lookup`
  - `constant_lookup`
  - `constant_name`
  - `constant_name_maps`
  - `constant_value`

Research notes:
- Generated protocol constant tables can share this common lookup format.
