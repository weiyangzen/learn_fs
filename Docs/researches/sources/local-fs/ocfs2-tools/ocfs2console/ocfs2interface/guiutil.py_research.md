# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/guiutil.py

Small GUI utility module.

Key functions:
- `set_props(obj, **kwargs)`
  - Calls `obj.set_property(k, v)` for each keyword.
- `format_bytes(bytes, show_bytes=False)`
  - Formats byte counts with suffixes `K`, `MB`, `GB`, `TB`.
  - Optionally includes exact byte count.
- `error_box(parent, msg)`
  - Shows modal GTK error dialog.
- `make_callback(obj, callback, sub_callback)`
  - Builds menu/toolbar callback wrappers that call object methods by name.

Compatibility:
- Exports `Dialog`.
  - Uses `gtk.Dialog` if it supports `set_alternative_button_order`.
  - Otherwise defines subclass with no-op `set_alternative_button_order`.

Notable details:
- `format_bytes` uses `K` for KiB-scale values and prints rounded integer values unless exact bytes requested.
