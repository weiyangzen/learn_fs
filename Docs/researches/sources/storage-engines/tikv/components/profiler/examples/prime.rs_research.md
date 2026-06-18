# sources/storage-engines/tikv/components/profiler/examples/prime.rs

Purpose: Provides a concrete profiling example that computes prime numbers while surrounding the hot loop with `profiler::start` and `profiler::stop`. It demonstrates both gperftools CPU profiling and Callgrind instrumentation workflows.

Important APIs/types/functions: `is_prime_number` checks primality using the prepared small-prime list and is marked `#[inline(never)]` to make profiles easier to inspect. `prepare_prime_numbers` builds a table of primes below 10,000 via a sieve. `main` builds the prime table, starts profiling to `./prime.profile`, counts primes from 2 to 49,999, stops profiling, and prints the count.

Control flow: The example first precomputes primes outside the profiled region. The profiled region is only the loop that calls `is_prime_number` for each candidate. This creates a stable, CPU-heavy workload suitable for validating profiler capture.

State and persistence behavior: State is local vectors and counters. gperftools mode writes `prime.profile`; Callgrind mode dumps through Valgrind's normal output mechanisms. There is no application persistence.

Dependencies and integration points: It depends only on the public `profiler` crate API. Cargo requires the `profiling` feature for this example, which ensures `profiler::start` and `stop` are real backend calls on Unix.

Risks: The primality check for values above 10,000 only tests divisibility by primes below 10,000; this is sufficient for the current range but not a general-purpose primality implementation for arbitrarily large values. Running under `valgrind cargo run` is explicitly unsupported because Callgrind detection targets the final example process.

Test signals: No assertions are present; build and manual execution are the validation signals. The printed prime count and generated profile/callgrind output indicate success.
