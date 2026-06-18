# File Research: sources/os/linux/linux/mm/kmsan/kmsan_test.c

## Role

KUnit test suite for KMSAN. It triggers expected uninitialized-memory, use-after-free, and no-report cases, captures console reports through the printk console tracepoint, and verifies report type and symbol matching.

## Report Capture Harness

- `observed` stores a spinlock-protected captured report header and flags.
- `probe_console()` watches console output for `BUG: KMSAN: `, copies the first matching line, and stops capture for the current test.
- `report_available()`, `report_reset()`, and `report_matches()` provide test assertions.
- `struct expect_report` records expected bug type and symbol.
- Matching strips exact offsets and module suffixes to avoid brittle comparisons.

## Helpers

- `check_true()`, `check_false()`, and `USE(x)` force conditional use of values so KMSAN reports undefined use.
- Expectation macros define no-report, uninitialized-value, and use-after-free expectations.
- `memcpy_noinline()` prevents compiler inlining when testing metadata propagation through `memcpy()`.
- `do_uninit_local_array()` deliberately writes uninitialized bytes into a selected array range.
- `fibonacci()` creates long origin chains.

## Covered Test Cases

- Heap allocation:
  - uninitialized `kmalloc()`.
  - initialized `memset()` after `kmalloc()`.
  - initialized `kzalloc()`.
- Stack and calls:
  - uninitialized stack variables.
  - initialized stack variables.
  - uninitialized function parameters.
  - multiple parameter propagation.
- Explicit checking:
  - `kmsan_check_memory()` on uninitialized local arrays.
- Virtual memory:
  - initialized pages mapped by `vmap()`.
  - `vmalloc()` buffers initialized by `memset()`.
  - guard-page edge safety for `memset()`.
- Use-after-free:
  - freed `kmalloc()` object.
  - freed single page.
  - freed high-order page tail.
- Per-CPU and printk:
  - uninitialized values through per-CPU storage.
  - uninitialized values passed to `pr_info()`.
- Copy and memset behavior:
  - initialized `memcpy()`.
  - uninitialized aligned-to-aligned copy.
  - uninitialized aligned-to-unaligned copy.
  - preservation of nonzero origins across initialized gaps.
  - `memset16()`, `memset32()`, `memset64()`.
- Origin and stack depot:
  - long origin-chain depth behavior.
  - stackdepot save/fetch/print round trip.
- Public API and nofault copy:
  - `kmsan_unpoison_memory()` equivalence with instrumentation.
  - `copy_from_kernel_nofault()` with uninitialized source.

## Suite Lifecycle

- `test_init()` resets captured report state before each test.
- `kmsan_suite_init()` registers the console tracepoint and disables `panic_on_kmsan`.
- `kmsan_suite_exit()` unregisters the tracepoint, synchronizes tracepoint removal, and restores `panic_on_kmsan`.
- The suite is registered as `kmsan` and carries GPL module metadata.

## Research Notes

The tests validate both positive and negative behavior across allocator hooks, compiler instrumentation, metadata propagation, origin handling, and reporting. The suite intentionally relies on instrumenting `kmsan_test.o`, unlike the runtime itself.
