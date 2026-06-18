# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/bosa.py

OCFS2 filesystem browser widget. It displays directory entries from an OCFS2 volume and metadata fields for the selected entry.

Key classes:
- `InfoLabel`
  - Monospace selectable label for one `ls.py` field.
  - Aligns and sizes based on field metadata.
- `Browser(gtk.VBox)`
  - Opens `ocfs2.Filesystem(device)`.
  - Displays current path label.
  - Builds a `gtk.TreeStore` of directory/file entries.
  - Sorts directories before files.
  - Lazily populates directories as tree rows are expanded.
  - Shows metadata labels using `ls.fields`.
- `TreeLevel(IdleBase)`
  - Wraps a directory iterator.
  - Runs incremental population through GLib idle callbacks.
  - Supports foreground/background priority when expanded/collapsed.

Dependencies:
- `ocfs2` Python C extension
- `gidle.Idle` fallback if `gobject.Idle` unavailable
- `ls.fields`
- PyGTK/Pango

Notable behaviors:
- Empty, loading, and error placeholder rows are inserted for UX feedback.
- Directory entries are loaded incrementally so large directories do not freeze the UI as much.
- `refresh()` clears old idle levels, opens filesystem, and starts root listing.

Notable issues:
- `tree_expand_row()` references `level` before assigning it in the branch where `info_obj` is already a `TreeLevel`; it should use `info_obj`.
- `get_fs_path()` assumes each iter maps to a dentry; placeholder rows may need parent fallback handling, which selection code partly manages.
