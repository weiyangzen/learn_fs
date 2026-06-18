# File Research: sources/virtualization/nbdkit/plugins/sh/sh.c

Front-end implementation of `nbdkit-sh-plugin`. It owns the selected script path, optional script-defined magic config key, and the global `subplugin` instance that points at the shared call functions.

`sh_config` requires the first parameter to be `script=`, resolves the script to an absolute path or reads an inline script from stdin into `$tmpdir`, invokes script `load`, then optionally reads `magic_config_key`. Later config parameters are passed to the script's `config` method, with bare-parameter remapping through the script-defined magic key.

Unload runs the script `unload` method best-effort, frees temporary resources, and releases stored strings. The registered nbdkit plugin delegates nearly all callbacks to `methods.c`, advertises magic key `script`, preserves errno, and uses a maximum parallel thread model subject to shell method negotiation.
