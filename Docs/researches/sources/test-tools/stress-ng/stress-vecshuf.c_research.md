## sources/test-tools/stress-ng/stress-vecshuf.c

Purpose: Implements `vecshuf`, stressing vector shuffle operations across 64-byte vectors of different element widths.

Important APIs/types/functions: `stress_vecshuf_info`, generated shuffle functions, builtin/manual shuffle shims, `stress_vecshuf_set_data`, `stress_vecshuf_set_mask`, `stress_vecshuf_check_data`, and `stress_vecshuf_call_method`; option `vecshuf-method` selects all or one width.

Control flow: allocates a vector data block, seeds original data, then each loop generates reversible rotate masks, applies two shuffles repeatedly so data should return to original order, records ops/bytes/duration, and verifies the final data equals the original.

State and persistence: vector data is anonymous mmap; static per-method metrics/byte counters accumulate until exit; no external resources.

Dependencies/integration: compiler vector support, optional `__builtin_shuffle`, target clones, SIGILL handling, metrics and debug logging.

Risks: manual fallback relies on mask values being in-range; x86 optimization level workarounds indicate compiler sensitivity. Verification catches irreversible shuffle/codegen faults.

Test signals: `VERIFY_ALWAYS`; logs instance-zero throughput and fails on any data mismatch.
