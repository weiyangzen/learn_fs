# sources/test-tools/fio/gclient.h

Purpose: gfio client header exposing the GUI client operation table, end-result renderer, and color constants used for read/write/trim graphs and labels.

Important APIs/types/functions: declares `extern struct client_ops gfio_client_ops`, `gfio_display_end_results(struct gfio_client *)`, and RGB constants `GFIO_READ_*`, `GFIO_WRITE_*`, and `GFIO_TRIM_*`.

Control flow: `gfio.c` passes `gfio_client_ops` to fio client connection/handler APIs and calls `gfio_display_end_results` from the Results menu path. The color constants are consumed when graph labels and colored ETA entries are created.

State and persistence behavior: no state is defined here, but the extern operation table is a process-global callback contract.

Dependencies/integration: requires `struct client_ops` and `struct gfio_client` from surrounding includes. It couples the GUI shell to `gclient.c`.

Risks and test signals: callback-table signature drift will break networking integration at compile time. Visual tests should confirm read/write/trim colors match between live ETA and result views.
