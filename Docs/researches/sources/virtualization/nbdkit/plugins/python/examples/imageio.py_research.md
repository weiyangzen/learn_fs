# File Research: sources/virtualization/nbdkit/plugins/python/examples/imageio.py

## Purpose
Example Python plugin for uploading/downloading images through oVirt ImageIO using nbdkit and qemu-img.

## Main Entry Points
- `config()` parses `transfer_url`, `connections`, `ca_file`, and `secure`.
- `config_complete()` requires `transfer_url`.
- `thread_model()` returns parallel mode.
- `open()` creates a queue-backed pool of `ImageioClient` connections.
- `close()` closes pooled clients.
- `get_size()`, `pread()`, `pwrite()`, `zero()`, and `flush()` borrow a client from the pool and call the corresponding ImageIO operation.

## Dependencies
Uses `ovirt_imageio.client.ImageioClient`, Python `queue`, `contextlib.contextmanager`, and nbdkit API version 2.

## Risks and Notes
The number of nbdkit threads should match the configured ImageIO connections to avoid avoidable blocking. The `boolify()` helper checks `0` as an integer instead of string `"0"`, so `secure=0` is not accepted as false. The example notes downloads are inefficient because extents are not reported.
