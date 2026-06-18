# File Research: sources/virtualization/nbdkit/plugins/python/plugin.c

Implements the `nbdkit-python-plugin` C bridge between nbdkit's plugin ABI and a user-provided Python script. It initializes Python, registers the built-in `nbdkit` Python module, loads the first `script=` parameter into `__main__`, validates required callbacks (`open`, `get_size`, `pread`), and honors script-declared `API_VERSION` up to version 2.

Each nbdkit callback acquires the Python GIL, looks up the corresponding Python function, calls it with nbdkit-style arguments, converts Python return values to C values, and routes exceptions through shared error handling. API v1 and v2 differ mainly in I/O signatures: v1 `pread` returns a buffer, while v2 writes into a memoryview and receives flags; write/flush/trim/zero similarly gain flags in v2.

The file supports lifecycle hooks, configuration, export listing/default export, preconnect, per-connection Python handles, size/block-size hints, capability callbacks, extents parsing from Python tuples, cache, FUA, fast-zero behavior, and fallback semantics for unsupported zero. Threading defaults to serialized requests unless Python overrides `thread_model`, while the registered plugin advertises a maximum parallel thread model.
