# File Research: sources/os/linux/linux/mm/gup_test.c

## Purpose

`gup_test.c` implements the kernel-side debugfs test and benchmark interface for GUP and PUP operations. It exposes `/sys/kernel/debug/gup_test` with ioctl commands that exercise fast GUP, slow GUP, fast pinning, slow pinning, long-term pinning, selected page dumping, and a stateful long-term pin/read/stop workflow.

## Major Responsibilities

- Dispatch `gup_test.h` ioctl commands through a debugfs file.
- Benchmark GUP/PUP acquisition and release times using `ktime_get()` and microsecond deltas.
- Allocate a temporary `struct page **` array for the requested user range.
- Take `mmap_read_lock()` for operations that require the slow path.
- Release returned pages correctly: `put_page()` for `FOLL_GET` style commands and `unpin_user_pages()` for `FOLL_PIN` commands.
- Verify that pin-oriented tests actually returned folios that appear DMA-pinned.
- Optionally dump selected pages for diagnostics.
- Maintain a global stateful long-term pin test buffer until explicit stop or file release.

## Main Ioctl Flow

`gup_test_ioctl()` accepts:

- `GUP_FAST_BENCHMARK`
- `PIN_FAST_BENCHMARK`
- `PIN_LONGTERM_BENCHMARK`
- `GUP_BASIC_TEST`
- `PIN_BASIC_TEST`
- `DUMP_USER_PAGES_TEST`
- `PIN_LONGTERM_TEST_START`
- `PIN_LONGTERM_TEST_STOP`
- `PIN_LONGTERM_TEST_READ`

The benchmark/basic/dump commands copy a `struct gup_test` from userspace, call `__gup_test_ioctl()`, and copy the updated timing and size data back. The long-term stateful commands are forwarded to `pin_longterm_test_ioctl()`.

`__gup_test_ioctl()` computes the number of pages from `.size`, allocates the page pointer array with `kvcalloc()`, optionally takes `mmap_read_lock_killable()`, and loops from `.addr` to `.addr + .size` in chunks of `.nr_pages_per_call`. Each iteration calls the selected GUP/PUP API and stops on short result or error. It records acquisition time in `.get_delta_usec`, updates `.size` to the processed byte count, performs optional verification/dumping, releases pages, and records release time in `.put_delta_usec`.

## Page Release and Verification

`put_back_pages()` matches release API to acquisition API:

- `GUP_FAST_BENCHMARK` and `GUP_BASIC_TEST` use `put_page()`.
- `PIN_FAST_BENCHMARK`, `PIN_BASIC_TEST`, and `PIN_LONGTERM_BENCHMARK` use `unpin_user_pages()`.
- `DUMP_USER_PAGES_TEST` chooses `unpin_user_pages()` or `put_page()` based on `GUP_TEST_FLAG_DUMP_PAGES_USE_PIN`.

`verify_dma_pinned()` checks only pin-oriented commands. It tests `folio_maybe_dma_pinned()` and, for the long-term benchmark, `folio_is_longterm_pinnable()`, warning and dumping the first failing folio.

`dump_pages_test()` treats `.which_pages[]` as 1-based page numbers relative to `.addr`. Out-of-range selections are zeroed with a warning, and selected pages are printed via `dump_page()`.

## Stateful Long-Term Pin Test

The file maintains:

- `pin_longterm_test_mutex`
- `pin_longterm_test_pages`
- `pin_longterm_test_nr_pages`

`pin_longterm_test_start()` copies `struct pin_longterm_test`, validates flags and page alignment, allocates the page array, and pins the whole range with `FOLL_LONGTERM`, optionally `FOLL_WRITE`, and optionally the fast API. It can loop because pin calls may return partial progress. On failure it calls `pin_longterm_test_stop()`.

`pin_longterm_test_read()` copies each pinned page to a user-provided destination using `kmap_local_page()`, `copy_to_user()`, and `kunmap_local()`.

`pin_longterm_test_stop()` unpins all held pages and frees the array. It is called by explicit ioctl and by `gup_test_release()`, so held long-term pins are cleaned up when the debugfs file is closed.

## Integration Points

The test file depends directly on the APIs implemented in `gup.c`, on `kmap_local_page()` from highmem/local-kmap infrastructure, and on debugfs for exposure. It is a diagnostic and benchmark utility, not a production memory-management primitive.
