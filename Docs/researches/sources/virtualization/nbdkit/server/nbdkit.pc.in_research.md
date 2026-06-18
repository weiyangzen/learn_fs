# File Research: sources/virtualization/nbdkit/server/nbdkit.pc.in

Purpose: Installed `pkg-config` template for compiling nbdkit plugins.

Fields:
- Defines install-time `prefix`, `exec_prefix`, `libdir`, and `includedir`.
- Exposes `plugindir` and `filterdir` under `@libdir@/nbdkit`.
- Provides package name, version, and description.
- Leaves `Requires`, `Cflags`, and `Libs` effectively empty.

Important note:
- The file explicitly documents that plugins do not link against a separate nbdkit library; symbols such as `nbdkit_error` are supplied by the main server binary when plugins are loaded.
