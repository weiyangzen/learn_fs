# File Research: sources/virtualization/nbdkit/plugins/curl/curl.c

Main nbdkit callback implementation for the curl plugin. It initializes libcurl globally, registers plugin callbacks, creates a lightweight per-connection `struct handle`, and uses one freshly allocated libcurl easy handle per NBD request.

Key behavior:
- Delegates global setup/teardown to `curl_global_init`, `worker_*`, `config_unload`, `scripts_unload`, and `display_times`.
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Allows multi-connection only for read-only connections because writable HTTP has no flush semantics.
- Implements `.get_size` by issuing a HEAD request through the worker thread, reading libcurl’s content length, and requiring `Accept-Ranges: bytes` for HTTP/HTTPS.
- Falls back from failed HEAD to GET only for HTTP 403, matching S3-style servers that reject HEAD but allow GET.
- Implements `.pread` with `CURLOPT_HTTPGET`, `CURLOPT_RANGE`, and `write_cb`.
- Implements `.pwrite` with `CURLOPT_UPLOAD`, `CURLOPT_RANGE`, and `read_cb`.

Important dependencies:
- `allocate_handle`, `free_handle`, and config state from `config.c`.
- `send_command_to_worker_and_wait` from `worker.c`.
- `do_scripts` from `scripts.c`.
- `update_times`/`display_times` from `times.c`.

Notable details:
- Read/write callbacks cap copied data to the requested NBD byte count even if curl/server supplies more.
- Error reporting goes through `display_curl_error`.
- `plugin.config_help` is assigned from a constructor to avoid non-constant initializer constraints.
