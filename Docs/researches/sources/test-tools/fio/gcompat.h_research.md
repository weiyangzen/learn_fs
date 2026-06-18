# sources/test-tools/fio/gcompat.h

Purpose: declares and maps GTK compatibility APIs for gfio across GTK2 and GTK3.

Important APIs/types/functions: for older GTK2, aliases `GtkComboBoxText` to `GtkComboBox`, declares text-combo helpers, and defines `GTK_COMBO_BOX_TEXT`. For GTK before 2.14 it defines inline `gtk_dialog_get_content_area` and `gtk_widget_get_window`. For GTK before 3 it declares allocated-size helpers. It defines `GFIO_DRAW_EVENT` as `"draw"` for GTK3 and `"expose_event"` for GTK2, and declares `gtk_widget_set_can_focus` for GTK before 2.18.

Control flow: preprocessor version checks select declarations/inlines at compile time, letting GUI sources use a mostly uniform API surface.

State and persistence behavior: no state beyond widget access performed by the declared functions.

Dependencies/integration: included by `gfio.h`, which spreads the compatibility layer throughout gfio. It must match implementations in `gcompat.c`.

Risks and test signals: incorrect version guards cause duplicate symbol definitions on newer GTK or missing APIs on older GTK. Build-matrix tests across GTK2.12/2.18/2.24-era headers and GTK3 are the primary signal, along with draw-event runtime smoke tests.
