# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/gidlemodule.c

Python 2 C extension exposing richer GLib idle source control as `gidle.Idle`.

Key type:
- `gidle.Idle`
  - Holds `GSource *idle`.
  - Tracks whether attached.
  - Supports instance dictionary and weakrefs.

Methods:
- `attach()`
  - Attaches idle source to default main context and returns source ID.
- `destroy()`
  - Destroys GLib source and marks object destroyed.
- `set_callback(callback, *args)`
  - Stores callback and args in a tuple.
  - Uses `g_source_set_callback`.

Properties:
- `__dict__`
- `priority`
- `can_recurse`
- `id`

Implementation details:
- `handler_marshal` calls Python callback and interprets truthiness as whether to keep source active.
- `destroy_notify` decrefs stored callback tuple.
- `CHECK_DESTROYED` raises `RuntimeError` if methods/properties are accessed after destroy.
- Module init registers `Idle` type.

Usage:
- `bosa.py` uses this as fallback when `gobject.Idle` is unavailable.

Notable details:
- Python 2 C API only: `PyInt`, `PyString`, `Py_InitModule`.
- Type has GC flags but no traverse function, only clear; acceptable for simple state but incomplete for cyclic GC precision.
