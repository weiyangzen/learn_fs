# sources/test-tools/fio/lib/memcpy.c

Purpose: standalone fio microbenchmark for comparing memory copy routines across block sizes.

Important APIs/functions: exported `fio_memcpy_test`; static test functions for `memcpy`, `memmove`, bytewise `simple_memcpy`, and a `hybrid` selector; `setup_tests`, `free_tests`, `get_test_mask`, and `list_types`.

Control flow: the entry point parses an optional comma-separated type list or help/list command, allocates two 32 MiB buffers, fills the source with deterministic random data, warms the CPU/data, then times repeated copies for sizes from 8 bytes to 512 KiB and prints MiB/s.

State/persistence: mutates static `tests[]` entries with shared source/destination buffers during a run. No persistent output beyond stdout.

Dependencies/integration: uses fio RNG, timing, spin, and OS helpers. Intended as a tool/helper path, not the main IO data path.

Risks/test signals: benchmark results are noisy and affected by compiler optimization, CPU state, cache warmth, and libc implementation. `t_hybrid` appears to use `simple_memcpy` for larger sizes and libc for smaller ones, which should be intentional or reviewed. Build/run tests should check allocation cleanup and type filtering.
