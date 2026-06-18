# sources/test-tools/fio/ghelpers.c

Purpose: reusable GTK widget helpers for gfio: framed read-only entries/labels, colored entries, spin buttons, tree-view columns, multitext rotating entries, and scrolled windows.

Important APIs/types/functions: exports `new_combo_entry_in_frame`, `new_info_entry_in_frame`, `new_info_entry_in_frame_rgb`, `new_info_label_in_frame`, `create_spinbutton`, `label_set_int_value`, `entry_set_int_value`, `tree_view_column`, `multitext_add_entry`, `multitext_set_entry`, `multitext_update_entry`, `multitext_free`, and `get_scrolled_window`. Internal `fill_color_from_rgb` converts floating RGB to `GdkColor`.

Control flow: widget factory functions create a frame, create the requested child, pack it into a caller-provided GTK box, and return the child widget. `tree_view_column` configures a text renderer, sorting, alignment, visibility, and appends the column. Multitext functions grow a string array, select/update text by index, and free all strings when the owning combo is destroyed.

State and persistence behavior: state is in GTK widget trees and `struct multitext_widget` arrays allocated with `realloc`/`strdup`. No disk persistence.

Dependencies/integration: depends on GTK, `gcompat.h`, and `ghelpers.h`. Used heavily by main gfio pages, result pages, ETA displays, and options dialogs.

Risks and test signals: `multitext_update_entry` assumes the index exists once `mt->text` is non-null; callers must allocate entries first. `multitext_free` sets unsigned `cur_text` to `-1`, producing a large value by design/accident. Tests should cover adding/updating/selecting entries, freeing empty and populated multitext widgets, column alignment/visibility flags, and GTK version compatibility.
