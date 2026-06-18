# File Research: sources/virtualization/nbdkit/plugins/sh/methods.c

Maps nbdkit plugin callbacks to shell script methods. It builds argv arrays of the form `script method [handle] [args...]`, calls through the global `subplugin` interface, interprets exit codes, and parses stdout into nbdkit callback results.

It handles lifecycle methods, thread model strings, export lists in multiple formats, default export extraction, open/close handles, export descriptions, size and block-size parsing, reads, writes with stdin payloads, boolean capability methods, FUA/cache tri-state strings, fast-zero fallback logic, flush/trim/zero/cache defaults, and extents parsing from text rows. Flags are rendered as comma-separated strings such as `fua`, `may_trim`, `req_one`, and `fast`.

The file preserves historical shell-plugin semantics, including non-required `open`, safe defaults for missing optional methods, and explicit errors when scripts return false where only success/error/missing makes sense.
