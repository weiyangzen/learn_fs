# File Research: sources/os/linux/linux/mm/memtest.c

## Purpose

Implements the early boot `memtest=` facility. It writes a sequence of test patterns over free memblock memory ranges, verifies the values, reserves detected bad physical memory ranges, and reports the total bad memory through proc meminfo.

## State and Patterns

State consists of:

- `early_memtest_done`, indicating at least one test pass ran.
- `early_memtest_bad_size`, accumulated bytes reserved due to failures.
- `memtest_pattern`, the boot-selected number of test passes.

The pattern table starts with zero so tested memory is left zeroed after a full cycle, then includes all-ones, alternating bit patterns, nibble patterns, and a final fixed signature.

## Boot Parameter

`early_param("memtest", parse_memtest)` parses:

- `memtest` without an argument as all available patterns.
- `memtest=<n>` as `n` passes.
- default `0`, meaning disabled.

## Test Flow

`early_memtest(start, end)` exits if disabled. Otherwise it runs `memtest_pattern` passes in reverse index order, wrapping through the pattern array.

`do_one_pass()` iterates all free memblock ranges via `for_each_free_mem_range()`, clamps each range to the requested physical interval, logs the tested range and pattern, and calls `memtest()`.

`memtest()` aligns the physical start to `sizeof(u64)`, writes the pattern to each word through the direct map, then rereads each word. Consecutive failing words are coalesced into bad ranges. Each bad range is passed to `reserve_bad_mem()`.

`reserve_bad_mem()` logs the bad range, reserves it with `memblock_reserve()`, and increments the bad-size counter.

## Reporting

`memtest_report_meminfo()` emits `EarlyMemtestBad` when procfs is enabled and a test ran. A nonzero bad size smaller than 1 KiB is rounded up to 1 KiB; zero means the test completed without detected bad memory.

## Invariants and Risks

The test only covers memblock free ranges, so already reserved memory is skipped. It relies on early direct-map access through `__va()` and runs before normal allocation. Detected failures are quarantined by memblock reservation, but this is a destructive write test over free memory and must run early enough that no live allocations occupy the tested ranges.
