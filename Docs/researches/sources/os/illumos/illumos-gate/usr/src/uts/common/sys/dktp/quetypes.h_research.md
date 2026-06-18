# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/quetypes.h

## Scope

Complete file read, 44 lines. This header defines the common queue backing data used by DKTP queue implementations.

## Public Surface

It defines:

- `struct que_data`: a queue mutex and `struct diskhd` queue head.
- `q_cnt` alias to `q_tab.b_bcount`.

## Behavior And Integration

Queue implementations use `que_data` to hold a synchronized disk buffer queue and count pending entries via the `diskhd` count field.

## Dependencies And Invariants

The header assumes `kmutex_t` and `struct diskhd` are visible. The `q_cnt` macro depends on the internal use of `b_bcount` as a queue count.

## Risks

Overloading `diskhd.b_bcount` as `q_cnt` is convention-based. Callers must hold `q_mutex` consistently when mutating queue state.
