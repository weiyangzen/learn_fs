# sources/user-network-fs/rclone/cmd/rc/rc.go

Purpose: implements `rclone rc`, a CLI client for calling remote-control endpoints on a running rclone instance.

Important APIs/state: globals for URL/auth, JSON/loop/output behavior, `parseFlags`, `ParseOptions`, `setAlternateFlag`, `errorf`, `doCall`, `run`, and `list`. It supports flags for URL, method, auth, headers, options, loop/timeout, JSON input/output, and Unix socket.

Control flow: command parses flags, maps alternate flags into rc config, then `run` either lists commands or parses command path plus key/value options. `doCall` builds an HTTP client/rc client, performs calls, handles status-code errors, optionally loops until success/timeout, and prints JSON or formatted output.

State/persistence: no persistent local state; network calls can mutate the remote rclone process depending on endpoint. Dependencies include rc client/config, JSON, HTTP, timeouts. Risks include credentials on command line, option parsing ambiguity, loop retry masking transient errors, and output format assumptions. Tests are likely in rc package/client tests.
