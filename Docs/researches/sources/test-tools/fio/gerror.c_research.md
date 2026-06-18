# sources/test-tools/fio/gerror.c

Purpose: centralizes gfio error and informational message presentation using GTK info bars and modal dialogs.

Important APIs/types/functions: exports `gfio_report_error(struct gui_entry *ge, const char *format, ...)` and `gfio_report_info(struct gui *ui, const char *title, const char *message)`. Internal `report_error` builds or updates the main-window error info bar, and `on_info_bar_response` destroys it on OK.

Control flow: `gfio_report_error` formats a `GError` from varargs, passes it to `report_error`, and frees it. `report_error` creates a `GTK_MESSAGE_ERROR` info bar with an OK button when none exists, adds a label to the main UI vbox, and shows the window. If an info bar already exists, it updates the label with a fixed failure message. `gfio_report_info` creates a modal dialog, adds a label, runs it, and destroys it.

State and persistence behavior: UI state is stored in `ui->error_info_bar` and `ui->error_label`; dismissal resets only the info-bar pointer. No disk persistence.

Dependencies/integration: depends on GTK, GLib `GError`, `gfio.h` structs, and is called from connection, file, option, and state error paths.

Risks and test signals: existing-error updates discard the specific new error message and replace it with a generic string. Dialogs are synchronous and block the GTK main loop until dismissed. Tests should trigger first and repeated errors, OK dismissal, info dialog display, and errors from worker/network callbacks with GTK thread locking already held.
