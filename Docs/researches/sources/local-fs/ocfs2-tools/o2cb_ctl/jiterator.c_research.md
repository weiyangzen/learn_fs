# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.c

Opaque iterator abstraction over arbitrary contexts, plus a built-in GLib `GList` adapter.

`j_iterator_new()` stores callbacks for `has_more`, `get_next`, and destruction. `j_iterator_new_from_list()` copies a `GList` container but not its data, then consumes and frees copied list nodes as callers iterate. `j_iterator_free()` invokes the configured destroy callback and frees the iterator object.
