# File Research: sources/virtualization/nbdkit/plugins/cc/cc.c

This plugin compiles a user-supplied C nbdkit plugin at configuration time, dynamically loads it, and forwards nbdkit callbacks to the loaded subplugin. The first parameter must be `script=<file>` or `script=-`; inline scripts are read from stdin into a temporary `.c` file when stdio is safe.

Configuration also accepts `CC`, `CFLAGS`, and `EXTRA_CFLAGS`; all other key/value pairs are saved and replayed into the subplugin's `.config`. `cc_config_complete` compiles the source to a temporary `.so`, loads it with `dlopen`, locates `plugin_init`, checks API version and required callbacks (`open`, `get_size`, `pread`), copies the plugin struct with size compatibility, then invokes the subplugin's load/config/config_complete.

The wrapper provides a broad callback surface: lifecycle, export negotiation, capabilities, block size, I/O, extents, cache, and cleanup. Missing optional callbacks either default to conservative answers or return appropriate errors/fallback signals. Thread model is delegated to the subplugin.

Risks and invariants: compiler command construction intentionally leaves compiler/flags unquoted but shell-quotes source/output paths. Running arbitrary compiler and plugin code is inherent. Temporary compiled output is unlinked after `dlopen`. Errno preservation is enabled so forwarded subplugin errors survive.
