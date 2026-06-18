# sources/test-tools/fio/printing.h

Purpose: declaration for gfio result printing.

Important APIs/types: declares `gfio_print_results(struct gui_entry *ge)`.

Control flow and state: no implementation; caller passes a gfio GUI entry used by `printing.c`.

Dependencies and integration: depends on a visible `struct gui_entry` declaration from gfio headers before use.

Risks: minimal API surface but tightly coupled to GTK/gfio types.

Test signals: gfio build and print action integration.
