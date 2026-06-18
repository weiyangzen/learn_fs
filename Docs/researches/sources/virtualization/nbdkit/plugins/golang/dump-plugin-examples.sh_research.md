# File Research: sources/virtualization/nbdkit/plugins/golang/dump-plugin-examples.sh

This shell test validates that built Go example plugins can be loaded by nbdkit.

Behavior:
- Runs with `set -e` and `set -x`.
- Iterates over `examples/*/nbdkit-*-plugin.so`.
- For each existing shared object, runs `../../nbdkit -f -v <plugin> --dump-plugin`.

Purpose:
- Confirms plugins were compiled correctly and can be loaded enough to answer `--dump-plugin`.
- Does not exercise read/write NBD I/O.
