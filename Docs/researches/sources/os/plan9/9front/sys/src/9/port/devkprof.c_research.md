# File Research: sources/os/plan9/9front/sys/src/9/port/devkprof.c

Purpose: kernel profiling device `#K`, collecting timer samples by program counter.

Exposed interface: directory with `kpdata` and `kpctl`. `kpctl` accepts `startclr`, `start`, and `stop`. `kpdata` returns big-endian 32-bit counters.

Core implementation: `kprofattach` lazily allocates a counter buffer covering `[KTZERO, etext)`, with one counter per PC offset plus special counters. `kprofinit` installs `_kproftimer` as the global profiling timer. `_kproftimer` increments elapsed-time count and either the PC bucket or out-of-range bucket; PCs in `spllo`/`splx` range use `m->splpc`.

Dependencies: kernel text symbols, timer callback hook `kproftimer`, and xalloc.

Research notes: this is simple but low-level. Review should focus on buffer sizing, architecture assumptions about PC range and counter width, and read alignment (`SZ` enforced at 4 bytes).
