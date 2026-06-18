# File Research: sources/os/bsd/dragonflybsd/sys/sys/exislock2.h

`exislock2.h` implements the inline existential lock API declared by `exislock.h`. It includes `globaldata.h` and `machine/thread.h`.

It provides `exis_init()`, `exis_setlive()`, per-CPU and current-CPU hold/drop helpers, `exis_poll()`, `exis_state()`, `exis_usable()`, `exis_freeable()`, `exis_cache()`, and `exis_terminate()`. The functions use per-CPU `gd_exislockcnt`, `gd_exisarmed`, `pseudo_ticks`, and `cpu_ccfence()` to avoid cacheline contention in normal access paths.

The API is subtle: CACHED objects can remain usable during a type-safe critical section even if they concurrently age to NOTCACHED; termination is staged over pseudo-ticks before destruction is safe.
