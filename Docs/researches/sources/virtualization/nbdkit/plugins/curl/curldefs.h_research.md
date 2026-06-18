# File Research: sources/virtualization/nbdkit/plugins/curl/curldefs.h

Shared internal header for the curl plugin.

Key contents:
- libcurl feature probes based on `CURL_AT_LEAST_VERSION`.
- Global configuration declarations: `url`, `connections`, scripts, renew intervals, debug flags.
- `struct handle`, the per-connection nbdkit handle.
- `struct curl_handle`, wrapping a `CURL *`, error buffer, transfer buffers, accept-range flag, copied headers, and associated worker command.
- `enum command_type` and `struct command` for worker-thread submission and completion signaling.
- Function declarations spanning `config.c`, `worker.c`, `scripts.c`, and `times.c`.

Notable details:
- Provides fallback `_Atomic` definition for older platforms.
- Defines `display_curl_error` macro to combine libcurl status and the easy-handle error buffer.
