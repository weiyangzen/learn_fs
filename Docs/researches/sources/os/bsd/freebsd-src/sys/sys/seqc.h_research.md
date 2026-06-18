# File Research: sources/os/bsd/freebsd-src/sys/sys/seqc.h

Sequence counter helper API for lockless readers with retry validation.

Key responsibilities:
- Imports public `seqc_t` from `_seqc.h` and defines kernel inline helpers.
- Provides writer entry/exit routines: `seqc_write_begin()` and `seqc_write_end()`.
- Provides reader helpers: `seqc_read_any()`, `seqc_read_notmodify()`, `seqc_read()`, `seqc_consistent()`, and no-fence consistency check.
- Provides sleepable writer variants that omit `critical_enter()`/`critical_exit()`.

Important patterns:
- Odd sequence values mark active modification through `SEQC_MOD`.
- Writers enter a critical section, increment to odd, apply a release fence, mutate, release fence again, then increment to even.
- Readers spin while the sequence is in modification and later verify the value did not change.
- The non-sleepable writer API prevents preemption during updates.

Research relevance:
- Key primitive for fast read-mostly kernel state where readers can tolerate retry but not locking.
