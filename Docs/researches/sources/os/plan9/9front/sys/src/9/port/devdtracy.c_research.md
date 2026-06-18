# File Research: sources/os/plan9/9front/sys/src/9/port/devdtracy.c

Purpose: kernel device `#Δ` for dtracy tracing support, gated by `*dtracy=` configuration.

Exposed interface: top-level `clone` and `probes`; each cloned tracing channel directory exposes `ctl`, `prog`, `buf`, `epid`, and `aggbuf`. `ctl` accepts `stop` and `go`; `prog` loads packed DTrace-like clauses.

Core implementation: `dtracyinit` enables tracing only if configured, allocates per-machine locks, and initializes tracing. `dtknew` allocates a `DTKChan`, stores it in `dtktab`, and creates a `DTChan`. `dtracyopen` creates a channel on `clone`, restricts non-directory channel files to eve, bumps refs, and attaches per-open aux string state. `dtracyclose` frees channels when refs drop to zero.

Read paths: `probesread` caches probe names, `epidread` caches enabled probe ids and record lengths, and `handleread` waits/polls for trace or aggregate buffer data. Writes compile programs with `prog` and control run state through `dtcrun`.

Dependencies: `<dtracy.h>` tracing runtime and kernel memory/locking adapters (`dtmalloc`, `dtfree`, `dtmachlock`, `dtpeek`, etc.).

Research notes: key areas are privilege checks, channel refcounting, cached string lifetime in aux, blocking read behavior, and safe address validation in `dtpeek`.
