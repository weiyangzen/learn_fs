# File Research: sources/os/plan9/9front/sys/src/9/port/taslock.c

Test-and-set spin lock and interrupt lock implementation.

Key responsibilities:
- Implements normal spin locks with `lock()`, `unlock()`, and `canlock()`.
- Implements interrupt-level locks with `ilock()` and `iunlock()`, saving/restoring interrupt priority state.
- Tracks lock owner process, CPU, caller PC, interrupt-lock status, and last lock fields for diagnostics.
- Prevents scheduling while normal locks are held through `up->nlocks`.
- Emits diagnostics for long lock loops, wrong unlock type, changed owner process, unlock of unlocked lock, and interrupt unlock while interrupts are low.
- Supports optional `LOCKCYCLES` instrumentation for max/cumulative lock hold cycles.

Dependencies:
- Uses architecture `tas`, `splhi`, `splx`, `islo`, `coherence`, scheduler, EDF fields, and process dump helpers.

Notable behavior:
- On uniprocessor EDF priority inversion, `lock()` yields by adjusting the admitted process deadline.
- `unlock()` may call `sched()` if scheduling was delayed while locks were held.
- `ilock()` spins by temporarily restoring the previous spl level while waiting, then reacquiring at high priority.
