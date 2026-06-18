# File Research: sources/virtualization/nbdkit/plugins/curl/worker.c

Background curl worker for asynchronous execution of curl easy handles through one curl multi handle.

Key behavior:
- `worker_get_ready` initializes the curl multi handle and sets max total connections when supported.
- `worker_after_fork` creates a self-pipe and starts the pthread worker.
- Main nbdkit threads submit `struct command *` over the pipe and block on a command-local condition variable.
- Worker loop alternates `curl_multi_perform`, finished-handle checks, and waiting on curl fds plus the self-pipe.
- Finished curl handles are removed from the multi handle and their command is retired with the curl status.
- `worker_unload` sends a STOP command, joins the thread, closes pipe fds, removes any remaining handles, and cleans up the multi handle.

Compatibility details:
- Uses `curl_multi_poll` when available, falling back to `curl_multi_wait`.
- Tracks active handles manually unless libcurl provides `curl_multi_get_handles`.
- Debug flag `-D curl.worker=1` traces command dispatch and retirement.

Concurrency model:
- One worker thread owns the curl multi handle.
- NBD request threads own command waiting and final error reporting.
