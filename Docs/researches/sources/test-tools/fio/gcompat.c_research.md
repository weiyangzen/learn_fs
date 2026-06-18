# sources/test-tools/fio/gcompat.c

Purpose: compatibility implementations for GTK APIs that differ across older GTK2/GTK3 versions.

Important APIs/types/functions: conditionally defines `gtk_combo_box_text_new`, append/insert/prepend/get-active-text wrappers for older GTK before 2.24, `gtk_widget_get_allocated_width`, `gtk_widget_get_allocated_height` for GTK before 3, and `gtk_widget_set_can_focus` for GTK before 2.18.

Control flow: compilation selects only the shims needed for the GTK version. Wrappers delegate to older GTK APIs or direct struct fields/macros.

State and persistence behavior: no persistent state. Functions return widgets or read/modify widget flags/allocation fields.

Dependencies/integration: includes GTK and `gcompat.h`. Used by gfio helpers and drawing code so the rest of the GUI can call newer API names unconditionally.

Risks and test signals: these shims rely on GTK2 struct internals such as `allocation` and `GTK_WIDGET_SET_FLAGS`. Test signals are builds against supported GTK2 minor versions and GTK3, combo-box text behavior, drawing-area size handling, and focus flag behavior.
