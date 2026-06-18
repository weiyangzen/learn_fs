# File Research: sources/os/plan9/plan9/sys/src/9/port/devkprof.c

Implements `#K/kprof`, a kernel PC sampling profiler. The namespace contains `kpdata` and `kpctl`.

On first attach, it allocates a count buffer covering kernel text from `KTZERO` to `etext`, bucketed by `LRES` bits. `kprofinit` installs `_kproftimer` into the global `kproftimer` hook.

When profiling is enabled, `_kproftimer` adds one tick in milliseconds to total time and either the PC bucket or the overflow bucket. PCs inside `spllo` to `spldone` are replaced with `m->splpc` to attribute time to the high-priority caller.

`kpctl` accepts `startclr`, `start`, and `stop`. `kpdata` reads big-endian 32-bit counters, aligned to four-byte cells. The data length is updated based on allocated bucket count.

The implementation is intentionally simple: one global profiler, no per-CPU separation, and fixed text-range bucketing.
