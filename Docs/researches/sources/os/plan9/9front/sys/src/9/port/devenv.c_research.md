# File Research: sources/os/plan9/9front/sys/src/9/port/devenv.c

Purpose: environment variable device `#e`, with per-process environment groups and a special configuration environment `#ec`.

Exposed interface: directory entries are environment variable names. `#e` is writable for the current environment group; `#ec` exposes the global configuration group and is writable by eve or its owner context. Files contain raw variable values.

Core implementation: `Egrp` stores entries in an indexed array plus hash chains. Qids combine a generation path and array index so stale Chans can be detected. `envcreate`, `envremove`, `envread`, `envwrite`, and `envopen` coordinate under the environment group RWLock. `envrealloc` tracks allocation and enforces `Maxenvsize` and `Maxvalsize` for non-configuration groups.

Lifecycle helpers: `newegrp` allocates a group, `envcpy` deep-copies one environment into another, `closeegrp` frees when refs drop, `ksetenv` writes from kernel code through the device interface, and `getconfenv` serializes the configuration environment as name/value strings.

Dependencies: `Egrp`/`Evalue` definitions from kernel data structures, process `up->egrp`, and Plan 9 namec/device operations.

Research notes: important areas are qid stale-entry protection, allocation accounting, permission differences between `#e` and `#ec`, `CRCLOSE` remove behavior, and hash/index consistency on create/remove.
