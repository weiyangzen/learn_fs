# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.c

## Role

`lgc.c` implements Lua's garbage collector: incremental mark-and-sweep, generational mode, weak-table handling, finalization, write barriers, object allocation links, emergency/full collections, and collector pacing.

## Main Responsibilities

- Allocates new collectable objects and links them to the appropriate GC list.
- Implements forward, backward, and prototype-specific write barriers.
- Marks roots: main thread, registry, metatables, and pending-finalization objects.
- Traverses tables, closures, prototypes, threads, userdata, strings, and upvalues.
- Handles weak-value, weak-key, all-weak, and ephemeron tables, including convergence of ephemeron propagation.
- Sweeps strings, finalizable objects, regular objects, open upvalues, thread stacks, and call-info lists.
- Separates finalizable userdata/objects into `finobj` and `tobefnz` lists and invokes `__gc` metamethods under protected calls.
- Controls state transitions across pause, propagate, atomic, sweep-string, sweep-udata, and sweep phases.
- Supports generational and incremental modes, mode switching, forced steps, ordinary steps, emergency collections, full collections, and free-all shutdown.

## Integration Points

This file coordinates with every collectable runtime type declared in `lobject.h`, closure/prototype management in `lfunc.c`, tables/strings, state management, the call layer for finalizers, and memory accounting in `lmem.c`.

## Risk Notes

Collector invariants are the main risk: black objects must not point to white objects while the invariant is active, weak tables need delayed clearing, and finalizers can resurrect objects or allocate. Emergency GC deliberately avoids finalizers.
