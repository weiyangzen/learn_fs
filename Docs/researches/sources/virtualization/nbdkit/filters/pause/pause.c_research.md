# File Research: sources/virtualization/nbdkit/filters/pause/pause.c

This filter provides a Unix-domain control socket that can pause and resume NBD request processing. Configuration requires `pause-control=SOCKET`, converted to an absolute path; `.config_complete` validates the socket path length, unlinks stale paths, creates/binds/listens on the socket, and starts the backend config-complete chain.

After fork, a background thread accepts one control connection at a time and reads single-byte commands: `p` pauses, `r` resumes, whitespace is ignored, and unknown commands respond with `X`. Responses are uppercase acknowledgements. Pause is implemented by locking a global `paused` mutex and then waiting on a separate request counter condition variable until all in-flight requests complete. Resume clears the paused state and unlocks the mutex.

Each request wrapper calls `begin_request`, delegates to the backend, and calls `end_request`. Wrapped operations include pread, pwrite, zero, trim, extents, and cache. `begin_request` first passes through the paused mutex and then increments `count_requests`; `end_request` decrements and signals waiters.

Correctness depends on balanced begin/end calls. Since the wrappers do not use cleanup guards, any future early return between begin and end would deadlock pause accounting. Current implementations delegate once and always call `end_request` after the delegate returns.
