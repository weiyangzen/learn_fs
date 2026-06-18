# File Research: sources/os/plan9/plan9/sys/src/cmd/map/index.c

Read fully: 86 lines, 4345 bytes. SHA-256 prefix: `cfdca8a35661375e`.

This file is the projection registry for the Plan 9 map program. It wraps projection constructors with uniform two-argument `Y...` adapters, then populates `struct index index[]` with projection name, constructor, parameter count, cut function, display flags, spheroid flag, and limb function.

Entries include projections such as `aitoff`, `albers`, `azequalarea`, `bonne`, `conic`, `guyou`, `hex`, `mercator`, `orthographic`, `sp_albers`, `tetra`, and others.

Integration: `map.c` likely looks up this table by projection name and uses associated cut/limb handlers.

Risk notes: many wrappers reference constructors not in this group. Table consistency depends on `map.h`’s `struct index` layout and projection function signatures.
