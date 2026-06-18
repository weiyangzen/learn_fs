# File Research: sources/os/bsd/openbsd-src/sys/sys/pclock.h

Defines a producer/consumer generation lock primitive.

Key contents:
- `struct pc_lock` with volatile generation counter.
- `PC_LOCK_INITIALIZER`.

Key APIs:
- `pc_lock_init`.
- Single-producer enter/leave: `pc_sprod_enter`, `pc_sprod_leave`.
- Multi-producer enter/leave: `pc_mprod_enter`, `pc_mprod_leave`.
- Consumer enter/leave: `pc_cons_enter`, `pc_cons_leave`.

Integration:
- Used by time/resource accounting code such as `struct tusage` and scheduler CPU-time accounting.
