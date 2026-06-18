# sources/test-tools/fio/sprandom.h

## Purpose
`sprandom.h` defines the state and API for SPRandom SSD steady-state offset generation.

## Important APIs, Types, And Functions
`struct sprandom_info` carries configuration (`over_provisioning`, `region_sz`, `cache_sz`, `num_regions`), invalidation probability/state (`invalid_pct`, `invalid_buf`, `invalid_capacity`, `invalid_count`, `current_region`, `curr_phase`), progress counters (`region_write_count`, `writes_remaining`), and fio random state. It declares `sprandom_init()`, `sprandom_free()`, and `sprandom_get_next_offset()`.

## Control Flow
The fio file/job initialization path calls `sprandom_init()`, offset selection repeatedly calls `sprandom_get_next_offset()`, and cleanup calls `sprandom_free()`.

## State And Persistence Behavior
The state struct is mutable and per-file. It does not describe durable storage; it controls one in-memory sequence of generated and replayed offsets.

## Dependencies And Integration Points
The header depends on `lib/rand.h` and `pcbuf.h`, and its function signatures depend on fio's `thread_data` and `fio_file` types from surrounding project headers.

## Risks And Edge Cases
The comments contain minor typos, but the larger risk is that callers must not copy `sprandom_info` shallowly because it owns heap pointers and staged buffer state. The API returns integer status but does not encode detailed terminal reasons.

## Test Signals
Compile tests should ensure all users see a consistent struct definition. Runtime tests should validate lifecycle pairing and that `sprandom_get_next_offset()` returns 1 only at expected end-of-sequence conditions.
