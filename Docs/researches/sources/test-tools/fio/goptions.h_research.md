# sources/test-tools/fio/goptions.h

Purpose: public header for gfio's option editor.

Important APIs/types/functions: declares `gopt_get_options_window(GtkWidget *window, struct gfio_client *gc)`, `gopt_init`, and `gopt_exit`.

Control flow: gfio initializes the option dependency tree at startup, opens an option window for the current client when the user selects Edit Job, and destroys option-editor global state at exit.

State and persistence behavior: no state is declared here; implementation maintains the dependency tree and mutates client option state during apply.

Dependencies/integration: includes GTK and relies on `struct gfio_client` from gfio context. It connects `gfio.c` menu actions to `goptions.c`.

Risks and test signals: initialization order matters: `gopt_init` must run after fio options are initialized and before any option window. Test signals include gfio startup/shutdown and opening/closing option dialogs repeatedly.
