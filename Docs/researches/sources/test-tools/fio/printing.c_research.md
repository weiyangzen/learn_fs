# sources/test-tools/fio/printing.c

Purpose: GTK/gfio print-operation support for results.

Important APIs/functions: `gfio_print_results()` is the exported entry point. Static callbacks `begin_print()`, `results_draw_page()`, `results_print_done()`, and `printing_error_dialog()` integrate with `GtkPrintOperation`.

Control flow: `gfio_print_results()` creates a print operation, restores previous settings/page setup if available, connects GTK signals, enables async printing, and runs the print dialog. `begin_print()` captures page dimensions and DPI and sets one page. `results_draw_page()` currently draws simple diagonal/crosshair test graphics and coordinate labels with Cairo. Error paths show a GTK message dialog and preserve settings on apply.

State and persistence: static `print_params` caches page setup, print settings, and page dimensions across calls. GTK reference counts are managed for settings, but page setup is stored as a pointer from the context.

Dependencies and integration: GTK, Cairo, gfio UI structures, and `draw_right_justified_text()`.

Risks: drawing looks like placeholder/test output rather than full fio results. Error-handling comment documents a hang when printing over an unwritable existing file. Cached `page_setup` lifetime should be reviewed because it is not explicitly referenced like settings.

Test signals: gfio print dialog, print-to-file success/failure, repeated print settings persistence, and visual output inspection.
