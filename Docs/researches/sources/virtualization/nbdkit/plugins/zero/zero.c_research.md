# File Research: sources/virtualization/nbdkit/plugins/zero/zero.c

Implements the minimal `zero` plugin.

Key behavior:
- `.open` returns `NBDKIT_HANDLE_NOT_NEEDED`.
- Thread model is `NBDKIT_THREAD_MODEL_PARALLEL`.
- `.get_size` returns `0`, so the export is zero-length.
- `.can_multi_conn` returns true because all connections observe the same empty/all-zero content.
- `.can_cache` returns `NBDKIT_CACHE_NATIVE`; no `.cache` implementation is needed because caching is a no-op.
- `.pread` exists only because a read callback is required by the plugin API; it logs an error if called unexpectedly.
- Sets `.errno_is_preserved = 1`.

Role:
- Serves as a tiny built-in-style plugin useful for tests, examples, and no-data exports.
