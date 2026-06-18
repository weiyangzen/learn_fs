# sources/test-tools/stress-ng/core-mmap.h

Purpose: public interface for mmap helpers and page-stat reporting used by memory-oriented stressors.

Important APIs/types: defines `stress_mmap_stats_t`, report flag constants for mapped/present/swapped/dirty/exclusive/unknown/null/contiguous pages, and declarations for mmap set/check/populate/unmap/stat helpers. It also provides `stress_mmap_stats_clear` as a zeroing inline.

Control flow: no runtime flow beyond the inline clear helper. It establishes the contract that callers allocate and pass `stress_mmap_stats_t` and choose report flags for `stress_mmap_stats_report`.

State/persistence: no state; the struct is caller-owned and accumulated through `stress_mmap_stats_sum`.

Dependencies/integration: relies on `stress_args_t`, fixed-width types, `memset`, `WARN_UNUSED`, and `core-mmap.c`. The flag names are consumed by stressors publishing memory metrics.

Risks: public flag spelling includes `STRESS_MMAP_REPORT_FLAGS_UKNOWN`, so correcting it would break callers unless aliased. Callers must provide valid mappings and compatible lengths.

Test signals: compile consumers with all flags, check zeroing through `stress_mmap_stats_clear`, and verify warning attributes catch ignored results for mapping/stat functions.
