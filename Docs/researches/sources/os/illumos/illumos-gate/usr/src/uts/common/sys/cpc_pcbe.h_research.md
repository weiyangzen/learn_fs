# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpc_pcbe.h

## Role

Defines the kernel-facing Performance Counter Backend interface used by CPC to support CPU-specific hardware counters.

## Key Interfaces

- `PCBE_VER_1`: required backend ABI version.
- `pcbe_ops_t`: backend operation table covering counter count, implementation identity, event/attribute listing, event coverage, overflow reporting, configuration, programming, stopping, sampling, and freeing.
- `pcbe_ops`: global selected backend operations pointer.
- `PCBE_IMPL_NAME_P4HT`: named implementation string for Pentium 4 HyperThreading.

## Behavior Notes

- Backends expose CPU counter capabilities through `pcbe_caps`, including overflow interrupt and precise overflow support.
- `pcbe_configure()` creates opaque per-counter backend configuration and can walk grouped configurations via a token.
- `pcbe_program()` must collect all grouped configs and program/start hardware counters.
- `pcbe_sample()` updates CPC-visible counter deltas.
- If overflow precision is unavailable, `pcbe_overflow_bitmap()` must conservatively report all counters overflowed.

## Dependencies

Includes `sys/inttypes.h` and `sys/cpc_impl.h`, particularly for integer types and `kcpc_attr_t`.

## Research Relevance

Useful for understanding illumos kernel performance counter plumbing and how CPU-specific drivers integrate with common accounting/profiling paths.
