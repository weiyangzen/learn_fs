## sources/distributed-fs/xrootd/src/XrdSys/XrdSysAtomics.hh

Purpose: defines legacy atomic-operation macros and C++11 atomic compatibility macros for low-level XrdSys code.

Important APIs/types/functions: `AtomicAdd`, `AtomicFAdd`, `AtomicCAS`, `AtomicDec`, `AtomicFAZ`, `AtomicFZAP`, `AtomicGet`, `AtomicInc`, `AtomicSub`, `AtomicFSub`, `AtomicZAP`, and `AtomicRet` map either to GCC `__sync_*` builtins under `HAVE_ATOMICS` or to caller-supplied locking via `AtomicBeg(Mtx)`/`AtomicEnd(Mtx)` and non-atomic expressions otherwise. `CPP_ATOMIC_TYPE`, `CPP_ATOMIC_LOAD`, and `CPP_ATOMIC_STORE` map to `std::atomic` only under C++11 or later.

Control flow: compile-time feature macros select true atomic builtins versus lock-assisted/non-atomic fallbacks.

State and persistence: no state is owned here. The macros mutate caller-owned variables and, in fallback mode, caller-owned mutexes.

Dependencies and integration: optionally includes `<atomic>`. Used by event polling and other utility code requiring portable counters or flags.

Risks: macro semantics are fragile. Fallback `AtomicCAS` does not return a boolean like the builtin version, `AtomicFAZ` expands to two statements, and fallback use is only safe if callers actually bracket access with locks. C++03 `CPP_ATOMIC_*` removes undefined-behavior protection.

Test signals: compile with and without `HAVE_ATOMICS`; exercise expression contexts, assignment contexts, compare-and-swap expectations, and fallback lock paths under thread sanitizer where possible.
