# File Research: sources/os/linux/linux/mm/kasan/sw_tags.c

## Role

Core runtime for software tag-based KASAN. It initializes tag mode, generates pointer tags, checks access ranges against software shadow tags, exports HWASan compiler ABI hooks, and handles tag mismatch callbacks.

## Key Functions

- `kasan_init_sw_tags()` seeds per-CPU PRNG state, initializes shared tag infrastructure, enables KASAN, and logs stacktrace state.
- `kasan_random_tag()` uses a per-CPU LCG seeded from cycle counters to generate probabilistic allocation tags.
- `kasan_check_range()` validates a memory range:
  - accepts zero-length access;
  - reports wrapped ranges;
  - ignores native kernel tag `0xff` to avoid false positives from kmap/page-address paths;
  - rejects addresses without metadata;
  - compares all covered shadow tag bytes against the pointer tag.
- `kasan_byte_accessible()` checks whether one tagged byte is accessible.
- Exports `__hwasan_load{1,2,4,8,16}_noabort`, `__hwasan_store{1,2,4,8,16}_noabort`, and variable-size load/store hooks.
- `__hwasan_tag_memory()` poisons a range with the supplied tag.
- `kasan_tag_mismatch()` decodes compiler access info into access size and write/read state, then reports.

## Dependencies

Uses software shadow mapping, tag helpers, exported compiler HWASan ABI, per-CPU state, random/cycle data, slab/KASAN internals, and stack collection controls.

## Research Notes

The PRNG is intentionally lightweight and non-atomic because software tag KASAN is a probabilistic debugging detector. Correctness depends on matching pointer tags to shadow tags, while security-grade unpredictability is explicitly traded off for runtime cost.
