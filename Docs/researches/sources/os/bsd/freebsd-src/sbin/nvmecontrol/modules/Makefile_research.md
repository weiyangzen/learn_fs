# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile

Builds vendor-specific `nvmecontrol` module subdirectories.

Key contents:
- Subdirectories: `intel`, `micron`, `samsung`, `wdc`.
- Includes `bsd.subdir.mk`.

Research notes:
- These modules provide vendor log-page decoders loaded by the `nvmecontrol` plugin mechanism.
