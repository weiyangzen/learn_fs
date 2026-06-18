# sources/test-tools/stress-ng/core-madvise.c

## Purpose

This file centralizes `madvise` option lists and helper calls for applying memory advice to mappings or to every mapping of a process. It supports random advice stress, common hint wrappers, THP collapse, no-hugepage behavior, KSM mergeability, and process-wide page advice on Linux.

## Important APIs, Types, And Functions

When `HAVE_MADVISE` is set, `madvise_options` and `madvise_options_elements` expose the supported advice constants. `madvise_random_options` is a safer random subset that excludes advice likely to zero or invalidate data used for checksum validation. Public functions are `stress_advice_check`, `stress_madvise_randomize`, `stress_madvise_random`, `stress_madvise_mergeable`, `stress_madvise_collapse`, `stress_madvise_willneed`, `stress_madvise_nohugepage`, and `stress_madvise_pid_all_pages`.

## Control Flow

Simple wrappers call `madvise` only when both `HAVE_MADVISE` and the target `MADV_*` constant are available; otherwise they return success. `stress_madvise_randomize` is gated by `OPT_FLAGS_MMAP_MADVISE`, selects a random safe advice, sanitizes it through `stress_advice_check`, and applies it. `stress_madvise_pid_all_pages` parses `/proc/$pid/maps`, applies one or random advice values to each mapping or page, and touches readable file-backed pages to pull them in.

## State And Persistence Behavior

The module owns no mutable state. It changes kernel VM advice for mappings in the current or target process. Process-wide advice can affect page residency, huge page behavior, fork inheritance, dump behavior, and reclaim behavior depending on advice.

## Dependencies And Integration Points

It depends on option flags, random utilities, memory page-size lookup, Linux `/proc/$pid/maps`, and platform `MADV_*` availability. It is used by mmap and memory stressors to vary kernel VM paths.

## Risks And Test Signals

Risks include destructive advice zeroing pages, SIGSEGV-inducing guard advice, parsing maps with unusual path fields, and advising ranges not valid in the current process. Test signals include no-op behavior without `OPT_FLAGS_MMAP_MADVISE`, wrapper success on unsupported advice, correct exclusion of dangerous random advice, and safe handling of inaccessible process maps.
