# sources/test-tools/stress-ng/core-mwc.c

Purpose: implements stress-ng's fast multiply-with-carry pseudorandom generator and helpers for random buffers, strings, and bounded values.

Important APIs/functions: `stress_mwc_reseed`, `stress_mwc_seed_set/get/default`, `stress_mwc32/64/16/8/1`, fallback `stress_mwc*modn`, `stress_rndbuf`, `stress_rndstr`, and `stress_uint8rnd4`.

Control flow: reseeding honors explicit `--seed`, deterministic `--no-rand-seed`, or mixes auxiliary vector randomness, time, process IDs, load average, resource usage, CPU/memory/filesystem/kernel traits, machine ID, and current time. Sub-word getters cache slices of 32-bit output. Buffer/string helpers stream bytes or base64url-safe characters. Fallback bounded generators use mask-and-reject loops.

State/persistence: single file-static `mwc` state with cached 16/8/1-bit fragments. Seed changes flush caches. The generator is not cryptographic and not thread-local.

Dependencies/integration: global `g_opt_flags`, settings, machine/system helper functions, bit operations, endian detection, and common attributes. Many stressors use this as their random source.

Risks: global mutable state is unsynchronized; deterministic runs depend on seed/cache flushing; random filenames rely on the restricted alphabet; modulo helpers differ by compile-time path.

Test signals: deterministic seed regression, cache flush after seed changes, endian behavior in `stress_uint8rnd4`, bounded output ranges, null buffer handling, and filename-safe string generation.
