# File Research: sources/os/bsd/freebsd-src/sys/sys/lockstat.h

Defines DTrace lockstat provider probes and lock profiling integration macros.

Key content:
- Declares `lockstat` SDT provider and probes for adaptive mutexes, spin locks, rw locks, sx locks, lockmgr locks, and thread spin events.
- Probe categories include acquire, release, spin, block, upgrade, downgrade, and disown.
- Defines `LOCKSTAT_WRITER` and `LOCKSTAT_READER`.
- Exposes `volatile bool lockstat_enabled`.
- With `KDTRACE_HOOKS`, `LOCKSTAT_RECORD*` macros emit SDT probes and profiling macros call lock-profile hooks plus emit the matching probe.
- Without `KDTRACE_HOOKS`, probe macros are empty while profiling hooks still call lock profiling where applicable.
- Provides `LOCKSTAT_PROFILE_ENABLED()` as runtime gating and declares `lockstat_nsecs()` with KDTrace hooks.

Research relevance:
- Bridges lock implementations with observability. Useful for tracing VFS and network-buffer lock contention without changing lock code.
- Works alongside `lock_profile.h`; DTrace and lock profiling can be independently relevant.

Cautions:
- Only active in kernel builds.
- Probe macros compile away when KDTrace hooks are absent, so instrumentation availability is build-dependent.
