# File Research: sources/virtualization/nbdkit/plugins/python/examples/url.py

## Purpose
Example Python plugin exposing a remote HTTP resource as a read-only NBD disk using range requests.

## Main Entry Points
- `config()` parses `url=`.
- `config_complete()` requires the URL.
- `thread_model()` returns parallel mode.
- `get_size()` performs a HEAD request, checks range support, and reads `Content-Length`.
- `pread()` issues a ranged GET for the requested bytes and copies the response into the nbdkit buffer.

## Dependencies
Uses Python `urllib.request` and nbdkit API version 2.

## Risks and Notes
The range-support check compares `headers.get_all('accept-ranges')` to an empty list; missing headers usually return `None`, so some non-range servers may pass this check until reads fail. The plugin does not implement write callbacks and is effectively read-only by capability omission.
