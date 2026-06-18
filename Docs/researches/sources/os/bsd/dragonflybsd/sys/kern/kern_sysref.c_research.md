# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sysref.c

Implements DragonFlyBSD’s `sysref` resource reference framework for cluster-addressable kernel resource structures. It combines reference counting, per-CPU sysid allocation, RB-tree lookup storage, and objcache-backed allocation.

Key structures and state:
- Per-CPU `sysref_array[MAXCPU]`, each with an RB tree and spinlock.
- RB tree generated over `struct sysref` keyed by `sysid`.
- `sysref_class` supplies object size, sysref offset, malloc type, objcache settings, optional ctor/dtor, and lifecycle ops.

Important behavior:
- `sysrefbootinit()` initializes per-CPU spinlocks and RB trees during boot.
- `sysref_init()` manually initializes static resources, assigns a CPU-encoded sysid, marks refcount as inactive/initializing, and inserts into the per-CPU RB tree.
- `sysref_alloc()` lazily creates the class objcache, obtains an object, verifies `SRF_PUTAWAY`, sets refcount to the negative initialization state, and zeroes non-sysref parts unless `SRC_MANAGEDINIT` is set.
- `sysref_ctor()` allocates a sysid, inserts the sysref into the per-CPU RB tree, marks `SRF_ALLOCATED | SRF_PUTAWAY`, then runs the class ctor.
- `sysref_dtor()` removes the sysref from its CPU-derived RB tree and runs the class dtor.
- `sysref_activate()` converts initialization refcounts into active positive refcounts.
- `_sysref_put()` handles normal decrements, active-to-terminating transition, termination callback invocation, and final objcache return or destruction depending on `SRF_SYSIDUSED`.
- `allocsysid()` exposes bare per-CPU sysid allocation.

Concurrency model:
- Per-CPU critical sections protect sysid allocation.
- RB tree mutation is protected by per-CPU spinlocks.
- Refcount transitions use atomic compare-and-set loops with `cpu_pause()` retry.
- Termination interlocks through class-provided lock/unlock/terminate operations.

Filesystem relevance:
- Not filesystem-specific, but it is a generic lifetime/identity mechanism that can back major kernel resources. Any VFS or filesystem object using `sysref` inherits this negative-refcount activation and termination lifecycle.
