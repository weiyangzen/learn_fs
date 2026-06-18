# File Research: sources/virtualization/nbdkit/plugins/python/examples/file.py

## Purpose
Example Python plugin that serves a local file as an NBD export.

## Main Entry Points
- `config()` parses and absolutizes `file=`.
- `config_complete()` requires the file parameter.
- `thread_model()` returns parallel mode.
- `open()` opens the file read-only or read-write.
- `get_size()` returns file size.
- `pread()` and `pwrite()` use `os.preadv` and `os.pwritev`.

## Dependencies
Uses Python `os`, nbdkit API version 2, and vector pread/pwrite support.

## Risks and Notes
The example does not implement `close()`, so fds rely on process cleanup. It assumes Python and platform support for `preadv`/`pwritev`.
