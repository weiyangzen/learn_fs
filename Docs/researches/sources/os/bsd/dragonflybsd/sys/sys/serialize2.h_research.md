# File Research: sources/os/bsd/dragonflybsd/sys/sys/serialize2.h

This kernel-only header defines inline helpers for acquiring and releasing arrays of `lwkt_serialize_t` serializers in a fixed order.

Key responsibilities:
- Rejects userland inclusion with `#error`.
- Includes kernel param/systm and `serialize.h`.
- Defines `lwkt_serialize_array_enter()`:
  - asserts starting index is valid
  - enters serializers from index `_s` through `_arrcnt - 1`
- Defines `lwkt_serialize_array_try()`:
  - tries serializers in ascending order
  - unwinds already acquired serializers in reverse order on failure
- Defines `lwkt_serialize_array_exit()`:
  - exits serializers in reverse order

Important invariants:
- Callers supply a starting index, enabling partial-array locking.
- Enter order is ascending; exit/unwind order is descending.
- KASSERT guards reject empty ranges.

Research notes:
- This header provides correct bulk acquisition patterns for non-recursive serializers.
