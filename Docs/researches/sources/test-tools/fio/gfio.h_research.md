# sources/test-tools/fio/gfio.h

Purpose: shared gfio data-model header for the GTK frontend. It defines main-window, per-job-tab, graph, ETA/probe, client, and result structures used across `gfio.c`, `gclient.c`, `goptions.c`, and helper modules.

Important APIs/types/functions: defines `struct probe_widget`, `struct eta_widget`, `struct gfio_graphs` and drawing dimensions, `struct gui`, `enum GE_STATE_*`, `enum GFIO_BUTTON_*`, `struct gui_entry`, `struct end_results`, `struct gfio_client_options`, and `struct gfio_client`. Declares `main_ui`, `gfio_view_log`, `gfio_set_state`, `clear_ge_ui_info`, graph font/color globals, and `GFIO_MIME`.

Control flow: the state enums drive button/menu sensitivity and represent the GUI client's lifecycle from new to connected, job sent/started/running/done. The structs are populated by UI construction in `gfio.c` and mutated by network callbacks in `gclient.c`.

State and persistence behavior: this header defines the in-memory state layout for gfio: GTK widget pointers, graph objects/labels, log/result models, pthread ids, client pointers, job file/host connection fields, option lists, accumulated disk-util and result data, and update-job status flags. Persistent effects are indirect, through GTK recent-manager metadata and fio server/client actions.

Dependencies/integration: includes GTK, compatibility shims, fio stat/thread option types, helper widgets, and graph types. It is the main coupling point among the gfio compilation units.

Risks and test signals: changes to these structs can break callback assumptions and memory ownership. The volatile update-job fields are used for cross-thread signaling but not a full synchronization primitive. Test signals include full gfio builds, state-transition UI tests, option-dialog update flows, and valgrind/sanitizer checks for result/client cleanup.
