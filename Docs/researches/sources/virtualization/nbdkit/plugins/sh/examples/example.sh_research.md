# File Research: sources/virtualization/nbdkit/plugins/sh/examples/example.sh

Full example Bash plugin for serving a local file. It demonstrates nbdkit shell-plugin method dispatch, exit-code conventions, `$tmpdir` usage, magic config key handling, config validation, thread-model opt-in, export listing/default export, per-connection handles, sizing, reads, writes, trim, zero, cache capability, extents, and dump-plugin metadata.

The script symlinks the configured file into `$tmpdir`, serves reads and writes with `dd`, uses `fallocate` for trim and zero where available, prefixes zero fallback errors with `ENOTSUP`, and prints simple extent rows. It is both runnable sample code and practical documentation for the shell method protocol.
