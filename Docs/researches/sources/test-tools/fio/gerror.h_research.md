# sources/test-tools/fio/gerror.h

Purpose: small gfio error-reporting API header.

Important APIs/types/functions: declares `gfio_report_error` for formatted entry-scoped errors and `gfio_report_info` for modal informational dialogs.

Control flow: callers route user-visible failures through these functions instead of directly constructing GTK info bars/dialogs.

State and persistence behavior: no state is declared here; implementations mutate GUI widget fields.

Dependencies/integration: requires `struct gui_entry` and `struct gui` declarations from `gfio.h` inclusion context.

Risks and test signals: signature changes affect most GUI error paths. Compile coverage and UI smoke tests for failure dialogs are sufficient for this header.
