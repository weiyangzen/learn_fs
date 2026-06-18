# sources/sync-backup/kopia/tools/node_env.sh

Purpose: configures a shell environment so Kopia's pinned Node.js installation under `tools/.tools` is first on `PATH`.

Control flow/APIs: resolves the script directory with `realpath $(dirname $0)`, extracts `NODE_VERSION` from `tools.mk`, logs both values, and prepends `$toolsdir/.tools/node-$node_version/bin` to `PATH`.

State/persistence: mutates only the current shell process environment when sourced. If executed as a subprocess, the exported `PATH` does not affect the caller.

Dependencies/integration: depends on `realpath`, `grep`, `head`, and `cut`; integrates with `tools.mk`'s Node version and installed node directory layout.

Risks/test signals: it does not `export PATH`, though shell assignment affects child commands from the same shell. It uses backticks and unquoted paths. Consumers must source it or otherwise run subsequent commands in the same process context.
