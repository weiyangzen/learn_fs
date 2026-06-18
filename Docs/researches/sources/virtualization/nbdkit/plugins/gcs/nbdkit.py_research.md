# File Research: sources/virtualization/nbdkit/plugins/gcs/nbdkit.py

This is a minimal Python stub for unit-testing `gcs.py` outside the nbdkit process.

Provided API:
- `FLAG_MAY_TRIM = 1`.
- `parse_size` converts a string to `int`.
- `debug` logs via Python logging.
- `set_error` is a no-op.

Integration:
- The real `nbdkit` Python module exists only inside nbdkit.
- This stub allows local tests in `gcs.py` to import expected names without running inside nbdkit.

Limitations:
- It intentionally implements only the attributes needed by the embedded tests.
