# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace_impl.h

This header defines DTrace’s private in-kernel implementation object model. It builds on `sys/dtrace.h` and describes probes, ECBs, actions, buffers, aggregations, speculations, dynamic variables, variable state, machine state, helper state, credentials, consumer state, providers, enablings, anonymous enablings, and low-level DTrace support routines.

Key contents:
- Core typedefs and constants such as `DTRACE_MAXPROPLEN` and `DTRACE_DYNVAR_CHUNKSIZE`.
- `dtrace_probe_t`: probe identity, ECB list, provider linkage, predicate cache, artificial frames, tuple strings, and hash-chain pointers.
- Probe lookup/hash support with `dtrace_probekey_t`, `dtrace_hashbucket_t`, and `dtrace_hash_t`.
- ECB model with `dtrace_ecb_t`, `dtrace_predicate_t`, `dtrace_action_t`, and `dtrace_aggregation_t`.
- Per-CPU `dtrace_buffer_t` design for principal, aggregation, speculative, switch, ring, and fill buffers.
- Aggregation buffer metadata with `dtrace_aggkey_t` and `dtrace_aggbuffer_t`.
- Speculation state machine and `dtrace_speculation_t`.
- Dynamic variable implementation: tuple keys, dynamic variable chunks, hash buckets, per-CPU free/dirty/rinsing/clean lists, and global dynamic-state state machine.
- Variable state for statically allocated globals, thread locals, clause locals, and dynamic variables.
- Per-probe-firing machine state `dtrace_mstate_t`, including scratch state, cached args/timestamps/stack data, access flags, current DIFO, and cached `getf()` result.
- Consumer activity state machine from inactive through warmup/active/draining/cooldown/stopped/killed.
- Helper action/provider/process state and helper tracing records.
- Credential visibility/action masks and `dtrace_cred_t`.
- `dtrace_state_t`: complete in-kernel consumer state, including ECBs, buffers, speculations, aggregation arena, counters, options, credentials, cleaner/deadman cyclic IDs, and retained enabling count.
- Provider/meta-provider runtime structures and retained enabling records.
- Anonymous enabling state.
- Toxic memory range definitions.
- Architecture/platform support function prototypes for argument access, stack capture, safe copy, register access, fault reporting, atomic CAS, time, assertion failure, and SPARC/x86-specific helpers.
- DTrace-local `ASSERT`/`VERIFY` overrides safe for probe context.

Dependencies:
- Includes `sys/dtrace.h`.
- Assumes kernel types such as `cred_t`, `file_t`, `vmem_t`, `cyclic_id_t`, `kthread_t`, `proc_t`, `pc_t`, `greg_t`, and `struct regs`.

Research notes:
- This is kernel-private and tightly coupled to `uts/common/os/dtrace.c` and ISA-specific DTrace code.
- The comments document major correctness constraints: per-CPU buffers to avoid sharing, atomic buffer switching with interrupts disabled, ring-buffer oldest-record tracking, nonblocking scratch allocation, asynchronous speculation cleanup, and dynamic-variable dirty/rinsing cleanup via `dtrace_sync()`.
- Dynamic variables deliberately avoid immediate chunk reuse to prevent cross-CPU stale references from observing unrelated new values.
- Filesystem relevance is observability and debugging: this is the implementation state behind DTrace probes that filesystem, VM, and storage code may fire or depend on for diagnostics.
