# sources/test-tools/fio/sprandom.c

## Purpose
`sprandom.c` implements fio's SPRandom offset generator for SSD steady-state style workloads. It models a physical device with over-provisioning, divides it into regions with a validity distribution derived from Desnoyers' SSD write-amplification model, and generates writes plus replayed invalidations to approximate region-level steady-state data validity.

## Important APIs, Types, And Functions
The public functions are `sprandom_init()`, `sprandom_get_next_offset()`, and `sprandom_free()`. Distribution helpers include `compute_waf()`, `compute_gc_validity()`, `compute_validity_dist()`, `sample_curve_equally_on_x()`, `linear_interp()`, `linspace()`, and `reverse()`. Capacity/layout helpers include `sprandom_physical_size()`, `estimate_inv_capacity()`, and `sprandom_setup()`.

Mutable write scheduling is centered on `struct sprandom_info` from `sprandom.h`: over-provisioning, region size/count, cache size, per-region invalid percentages, a two-phase `pc_buf`, invalid counts per phase, current region, current phase, region write counts, remaining writes, and random state. `sprandom_add_with_probability()` probabilistically stages offsets for later invalidation; `sprandom_get_next_offset()` alternates between replaying invalid offsets and consuming the file LFSR.

## Control Flow
`sprandom_init()` exits early when the job option is disabled. Otherwise it allocates `sprandom_info`, determines logical size from file size and requested I/O size, computes physical `td->o.io_size`, stores the fio random state, and calls `sprandom_setup()`. Setup computes the validity distribution, converts validity to invalid percentages at `PCT_PRECISION`, validates optional cache size against region size, estimates invalid buffer capacity with a six-sigma margin, allocates the `pc_buf`, and initializes region/phase counters.

During generation, `sprandom_get_next_offset()` first replays pending invalid offsets either before entering the next region or, when cache deferral is configured, at the end of the current region. When region writes are exhausted, it prints invalidation diagnostics, flips phase, commits staged offsets, advances `current_region`, and sets `writes_remaining` to region capacity minus pending invalidations for that phase. It then pulls a fresh LFSR offset, decrements writes remaining, and may stage that offset for future invalidation based on the current region's invalid probability.

## State And Persistence Behavior
All state is in-memory per file through `f->spr_info`. The generator mutates `td->o.io_size` to the modeled physical size. `invalid_buf` is a staged/committed two-phase buffer, so generated offsets depend on prior calls and cannot be recomputed statelessly from a position alone. There is no persistent state across process runs.

## Dependencies And Integration Points
The file depends on fio job options (`sprandom`, `spr_over_provisioning`, `spr_num_regions`, `spr_cache_size`, block size), `struct fio_file`, the file LFSR, `pcbuf`, fio random helpers, logging buffers, `bytes2str_simple()`, math functions, and pow2 utilities. It integrates with file offset selection by attaching `sprandom_info` to `fio_file`.

## Risks And Edge Cases
`compute_waf()` divides by over-provisioning and assumes valid nonzero input. `compute_gc_validity()` asserts WAF > 1.0. `compute_validity_dist()` calls `reverse(validity_distribution, n_regions)` at `out`; if allocation failed before `validity_distribution` is assigned, this can pass NULL with nonzero size and dereference it. Several allocation failures in `sprandom_setup()` free only part of the initialized state; `invalid_buf` is not freed on all later setup failures. `sprandom_free()` uses `free(info->invalid_buf)` even though allocation is through `pcb_alloc()`, which is correct only if `pcbuf` promises libc-compatible allocation. Buffer capacity overflow asserts rather than returning an error.

## Test Signals
Tests should validate distribution generation for one, many, and invalid region counts; over-provisioning boundary handling; cache size rejection; deterministic offset streams for a fixed seed; invalidation percentages within statistical tolerance; LFSR exhaustion with and without cache deferral; and leak/error-path behavior under forced allocation failures.
