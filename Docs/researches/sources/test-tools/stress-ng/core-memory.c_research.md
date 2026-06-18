# sources/test-tools/stress-ng/core-memory.c

## Purpose

This file provides cross-platform memory information and memory-management helpers for stress-ng. It reports page size, free/total memory and swap, SHMALL, low-memory conditions, physical memory size, allocation usage, anonymous VMA names, swapoff, address readability, per-PID memory usage, KSM toggling, and kernel memory compaction.

## Important APIs, Types, And Functions

Public APIs are `stress_memory_page_size_get`, `stress_memory_info_get`, `stress_memory_limits_get`, `stress_memory_free_get`, `stress_memory_ksm_merge`, `stress_memory_low_check`, `stress_memory_phys_size_get`, `stress_memory_usage_get`, `stress_memory_address_align`, `stress_memory_anon_name_set`, `stress_memory_swap_off`, `stress_memory_readable`, `stress_memory_usage_by_pid_get`, and `stress_memory_compact`.

## Control Flow

`stress_memory_info_get` tries Linux `sysinfo`, then FreeBSD sysctl counters, NetBSD `uvmexp2`, and macOS Mach VM stats, falling back to zeros and `-1`. `stress_memory_low_check` lazily computes an OOM avoidance threshold, compares current and previous free memory/swap, checks requested allocation headroom, and if low memory is detected drops caches and enables KSM merge. `stress_memory_compact` writes to `/proc/sys/vm/compact_memory` only when the option is enabled, and disables repeated attempts after failure.

## State And Persistence Behavior

Static state caches page size, previous free memory/swap, low-memory threshold, KSM previous flag, and compaction skip status. External side effects include KSM enabling, cache dropping, VM compaction, swapoff, anonymous VMA naming, and pipe-based memory readability probes.

## Dependencies And Integration Points

The module depends on filesystem helpers for `/proc` and `/sys` reads/writes, BSD sysctl helpers, formatting/logging, option settings (`oom-avoid-bytes`, `compact-memory`), page-size consumers, and platform APIs such as sysinfo, Mach host statistics, prctl `PR_SET_VMA`, and swapoff.

## Risks And Test Signals

Risks include overflow in memory unit multiplication, platform counters with different semantics, low-memory false positives, global side effects from cache dropping/KSM/compaction, and pipe writes with very large readable checks. Test signals include page-size fallback, Linux/BSD/macOS memory info paths, low-memory threshold behavior, KSM write suppression when flag unchanged, per-PID statm conversion, swapoff EINTR retry, and compaction failure suppression.
