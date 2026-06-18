# File Research: sources/virtualization/nbdkit/server/main.c

Purpose: Main server entry point. Parses CLI options, initializes process-wide state, loads plugins/filters, configures backends, selects serving mode, and drives shutdown cleanup.

Global configuration:
- Defines the command-line globals declared in `internal.h`, including TLS settings, logging mode, service mode, socket/run/stdin state, thread count, timeout, read-only mode, and backend chain `top`.
- Maintains temporary random Unix socket path state for `-U -` and implied `--run`.

Startup flow:
- Verifies stdio is open, initializes Winsock on Windows, and initializes thread-local state.
- Defaults TLS to on when compiled with GnuTLS, off otherwise.
- Reads socket activation state before option parsing.
- Parses all short and long options from `options.h`.
- Validates incompatible mode combinations such as `-s` with `--run`, oldstyle with `--tls=require`, and socket activation with explicit socket options.
- Opens logging, initializes TLS, optionally configures exit-with-parent, computes service mode and URI.

Plugin/filter loading:
- First non-option argument is the plugin.
- Short plugin/filter names are resolved to `plugindir/nbdkit-<name>-plugin.<soext>` or `filterdir/nbdkit-<name>-filter.<soext>`.
- Executable script plugins in `plugindir` are exec’d directly.
- `open_plugin_so` uses `dlopen`, resolves `plugin_init`, and calls `plugin_register`.
- `open_filter_so` resolves `filter_init` and wraps the current chain with `filter_register`.
- Filters are applied in reverse collected order so command-line order matches request-processing order.

Configuration:
- Parses remaining arguments as `[key=]value` or `@PATH`.
- Bare values use the backend magic config key, or legacy first-argument `script` behavior when no magic key exists.
- `@PATH` files are read line by line, ignoring blank/comment lines, and nested relative `@PATH` entries resolve relative to the including file.
- Configuration keys are interned because plugin config receives pointers that must live for process lifetime.

Mode handling:
- `--help`, `--version`, and `--dump-plugin` load backends as needed, emit information, then clean up and exit.
- `--print-uri` emits URI information before stdio is sanitized.
- `switch_stdio` saves stdin/stdout for `-s`/`--run`, then redirects stdin/stdout to `/dev/null`.

Serving:
- `start_serving` sets up quit handling and signals, optionally locks memory for `--swap`, then serves through one of:
  - socket activation
  - stdin/stdout single connection
  - Unix socket
  - AF_VSOCK
  - TCP/IP
- Common socket modes may run a captive command, change user/group, fork into background, write pidfile, call `after_fork`, then accept incoming connections.
- Stdin mode directly calls `handle_single_connection(saved_stdin, saved_stdout)`.

Cleanup:
- Runs backend cleanup and free, releases sockets/URI/pidfile/random FIFO/TLS/quit pipe/socket activation/interned strings.
- Returns instead of exiting to support libFuzzer builds.
