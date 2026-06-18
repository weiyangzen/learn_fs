# File Research: sources/os/bsd/freebsd-src/sys/sys/lockmgr.h

Defines the lockmgr lock API, state encoding, operations, attributes, and assertions.

Key content:
- Low bits in `lk_lock` encode shared/exclusive waiters, spinners, share mode, and writer recursion.
- Macros decode holder, sharer count, unlocked state, and disowned kernel ownership.
- Kernel API includes `__lockmgr_args`, direct shared/exclusive/unlock helpers, init/destroy, recursion/share toggles, disown, status, debug chain, and printinfo.
- Inline wrappers accept mutex or rwlock interlocks and pass their embedded `lock_object`.
- Public macros include `lockmgr`, `lockmgr_args`, `lockmgr_args_rw`, `lockmgr_disown`, `lockmgr_recursed`, and `lockmgr_assert`.
- `lockinit()` flags define recursion, no-duplicate, no-profile, no-share, no-witness, quiet, vnode, and new behavior.
- Operation flags define shared/exclusive/release/upgrade/downgrade/drain/try-upgrade.
- Assertion flags map to generic lock assertions.

Research relevance:
- Lockmgr is heavily used by vnode and filesystem code, including mount locks in `mount.h`.
- Its state encoding matters when researching vnode lock behavior, shared/exclusive transitions, and recursion.
- Requires `LOCK_FILE` and `LOCK_LINE`, so callers must include `sys/lock.h` first.

Cautions:
- Some flags are operation attributes, some init-only, and some operation types; `LK_TOTAL_MASK` separates these classes.
- Comment has legacy spelling but API names are authoritative.
