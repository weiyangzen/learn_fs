# sources/sync-backup/syncthing/cmd/syncthing/cli/utils.go

Purpose: shared helpers for `syncthing cli` HTTP responses, pretty printing, file saves, config loading, and path normalization.

Important APIs/functions: `responseToBArray`, `emptyPost`, `indexDumpOutputWrapper`, `indexDumpOutput`, `saveToFile`, `getConfig`, `prettyPrintJSON`, `prettyPrintResponse`, and `normalizePath`.

Control flow: response helpers read and close bodies. Dump helpers fetch REST responses and pretty-print JSON or save raw response bytes to a server-provided filename. `getConfig` fetches `system/config` and unmarshals into `config.Configuration`. `normalizePath` cleans and converts paths to slash-separated form.

State and persistence: `saveToFile` writes local files; `getConfig` and pretty print are read-only; empty posts trigger API side effects.

Dependencies/integration: used by most CLI subcommands and depends on JSON, MIME `Content-Disposition`, filesystem paths, and Syncthing config.

Risks and test signals: pretty printing requires valid JSON, so non-JSON REST responses will error. `saveToFile` uses the server's filename without additional path sanitation. No direct tests.
