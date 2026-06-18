# File Research: sources/virtualization/nbdkit/plugins/S3/nbdkit.py

This is a small Python stub of the real `nbdkit` module for unit testing `S3.py` outside the nbdkit process. It defines a logger, `FLAG_MAY_TRIM`, `parse_size`, `debug`, and `set_error`.

The stub intentionally implements only the minimum needed by the local tests in `S3.py`. It does not provide constants such as `THREAD_MODEL_PARALLEL`, `CACHE_NONE`, or `FUA_NATIVE` used by normal plugin registration paths, so it is not a full emulation of the runtime module.

Its purpose is test isolation: code paths that only need parsing, debug logging, or trim flags can run under standard Python.
