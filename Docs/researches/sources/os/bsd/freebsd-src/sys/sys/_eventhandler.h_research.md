# File Research: sources/os/bsd/freebsd-src/sys/sys/_eventhandler.h

Private eventhandler type definitions.

Key elements:
- Defines `struct eventhandler_entry` with TAILQ linkage, priority, and callback argument.
- Defines `eventhandler_tag`.
- Provides declaration macros for predeclared eventhandler lists and typed eventhandler entries.

Dependencies:
- Includes `sys/queue.h`.

Research notes:
- This header supplies the lightweight shared structure layer for `eventhandler.h`.
- Direct list declarations are intended to avoid global-list lookup overhead for high-frequency events.
