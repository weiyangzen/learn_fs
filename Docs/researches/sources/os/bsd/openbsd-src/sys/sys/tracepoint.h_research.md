# File Research: sources/os/bsd/openbsd-src/sys/sys/tracepoint.h

Provides kernel tracepoint macros. When `_KERNEL` and `NDT > 0`, it includes DTrace-style `dtvar.h` and maps `TRACEPOINT`/`TRACEINDEX` to static/indexed DT enter macros.

When dynamic tracing is not built, both macros compile away. This lets kernel code keep trace hooks without runtime or build-time dependencies when tracing support is absent.
