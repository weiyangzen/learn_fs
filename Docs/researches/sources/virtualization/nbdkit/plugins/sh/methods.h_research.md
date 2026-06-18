# File Research: sources/virtualization/nbdkit/plugins/sh/methods.h

Declares the shell method dispatcher callbacks consumed by `sh.c`. It covers lifecycle, connection/export callbacks, sizing, block size, I/O, capability checks, FUA/cache/fast-zero logic, extents, and cache.

This header exposes the shell plugin's nbdkit-facing callback surface while leaving parsing and script invocation details in `methods.c`.
