# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rangelock.c

## Purpose
Implements FreeBSD scalable range locks used by subsystems that need byte/range-granular read/write exclusion, commonly for file or VM-object style ranges. The implementation starts in a compact “cheating” mode and falls back to a precise SMR-protected range queue when conflicts require real range tracking.

## Major Responsibilities
- Initializes/destroys `struct rangelock` with `rangelock_init()` and `rangelock_destroy()`.
- Provides read/write lock and trylock entry points: `rangelock_rlock()`, `rangelock_tryrlock()`, `rangelock_wlock()`, and `rangelock_trywlock()`.
- Releases locks with `rangelock_unlock()`.
- Supports callers that may recursively acquire on the same lock through `rangelock_may_recurse()`.
- Provides DDB inspection under `show rangelock`.

## Cheating Mode
- Controlled by debug tunable `debug.rangelock_cheat`.
- A newly initialized lock behaves like a compact whole-object read/write lock using bits in `lock->head`.
- Multiple readers can enter without allocating queue entries.
- A conflicting request sets `RL_CHEAT_DRAINING`, waits for existing cheat holders to leave, wakes sleepers, and transitions to precise non-cheat mode.
- Trylocks in cheat mode fail without draining when a conflict exists.

## Precise Range-Lock Mode
- Uses `struct rl_q_entry` queue entries allocated from an SMR UMA zone.
- Queue entries store start/end offsets, read/write flags, next links, deferred-free links, and invariant owner thread.
- Implements sorted insertion and conflict detection based on range overlap and read/read compatibility.
- Marked next pointers represent logically removed entries; dead entries are physically unlinked and freed after SMR exit.
- Read validation only checks later conflicting writers; write validation checks prior overlapping entries before the writer.

## Locking and Memory Model
- Uses atomic pointer operations for queue head/next updates.
- Uses SMR sections around queue traversal and CAS insertion/removal.
- Uses sleep queues on `lock->sleepers` for precise-mode conflicts and on `lock->head` for cheat-mode draining.
- Drops and reacquires Giant around sleeps.
- `rangelock_unlock_int()` marks the entry, clears sleeper state, and broadcasts waiters.

## Key Interfaces
- `rangelock_init(struct rangelock *)`
- `rangelock_destroy(struct rangelock *)`
- `rangelock_rlock(lock, start, end)`
- `rangelock_tryrlock(lock, start, end)`
- `rangelock_wlock(lock, start, end)`
- `rangelock_trywlock(lock, start, end)`
- `rangelock_unlock(lock, cookie)`
- `rangelock_may_recurse(lock)`

## Notable Edge Cases
- Cheat-mode cookies are sentinel pointer values rather than allocated queue entries.
- Recursive/conflicting acquisition by the same thread is asserted against in precise mode.
- Trylock failure after insertion may leave the entry marked and defer freeing until safe.
- Destroying a non-cheat lock drains marked entries and waits if any live entry remains.
