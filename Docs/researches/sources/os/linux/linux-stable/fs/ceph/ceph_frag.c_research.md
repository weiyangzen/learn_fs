# File Research: sources/os/linux/linux-stable/fs/ceph/ceph_frag.c

## Purpose

`ceph_frag.c` implements comparison for Ceph fragment identifiers.

## Main Function

`ceph_frag_compare(__u32 a, __u32 b)`:
- Extracts fragment value with `ceph_frag_value()`.
- Compares fragment values first.
- If values match, compares fragment bit counts with `ceph_frag_bits()`.
- Returns `-1`, `1`, or `0` for ordered comparison.

## Dependencies

- `linux/ceph/types.h` for Ceph fragment encoding helpers.
- Used anywhere Ceph fragment ids need stable ordering, commonly directory-fragment maps or ordered containers.

## Notes

The comparator orders by fragment value before precision/bit count, making it a small utility for deterministic fragment sorting.
