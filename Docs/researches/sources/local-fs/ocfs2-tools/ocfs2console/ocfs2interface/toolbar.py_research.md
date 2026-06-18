# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/toolbar.py

## Purpose
Defines the GTK toolbar used by `ocfs2console`, with mount, unmount, refresh, and partition-name filter controls.

## Main Behavior
- `toolbar_data` declares three toolbar buttons: `Mount`, `Unmount`, and `Refresh`.
- `Toolbar.get_widgets()` builds a `gtk.Toolbar`, wires callbacks through `guiutil.make_callback()`, stores returned toolbar items by callback name, and appends a filter box.
- `Toolbar.get_filter_box()` creates a horizontal `Filter:` label plus `gtk.Entry`.
- `main()` is a small standalone GTK smoke/demo harness that creates dummy callbacks and displays the toolbar.

## Dependencies
- GTK 2 Python bindings via `import gtk`.
- `guiutil.make_callback`, expected to adapt `window.<callback>` plus optional sub-callback names into GTK callbacks.
- The parent window object is expected to expose `mount`, `unmount`, and `refresh` methods.

## Notes
The file is UI glue only; it performs no OCFS2 operations directly. It returns `(toolbar, items, entry)` so callers can later enable/disable toolbar items and inspect/filter text.
