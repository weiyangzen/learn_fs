# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/cumulative_stats.hpp

Purpose: Implements one-pass cumulative statistics for FOA instrumentation.

Important APIs, types, and functions: Defines `sequence_stats_data`, `welfords_algorithm`, `sequence_stats_summary`, `cumulative_stats<N>`, and thread-safe `concurrent_cumulative_stats<N>` when threads are enabled.

Control flow: `add` increments a sample count and uses MP11 tuple transformation to apply Welford's algorithm to N sequences. `get_summary` returns count, average, biased variance, and standard deviation for each sequence. Count wraparound resets the accumulator.

State and persistence behavior: Stores count and per-sequence running mean/prior mean/sum-of-squares. The concurrent variant protects the base stats with `rw_spinlock` and `std::lock_guard`.

Dependencies and integration points: Used when `BOOST_UNORDERED_ENABLE_STATS` is set in FOA table cores. Depends on Boost.MP11 tuple support and optionally `rw_spinlock`.

Risks: Variance is biased by design (`s / n`). Concurrent copies take a lock, but readers should still treat stats as diagnostic, not synchronization state.

Test signals: Numeric tests should check averages/variance/deviation, reset, wraparound behavior where practical, and concurrent add/get under `BOOST_HAS_THREADS`.
