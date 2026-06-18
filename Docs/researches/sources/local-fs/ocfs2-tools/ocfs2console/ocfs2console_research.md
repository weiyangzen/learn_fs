# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console

Python 2 executable entrypoint for the OCFS2 GUI console.

Behavior:
- Imports `process_args()` from `ocfs2interface.about`.
- Supports node-config-only mode via parsed arguments.
- Temporarily converts warnings to errors during `gtk` import to catch no-display initialization failures.
- On GTK initialization failure:
  - Prints a specific X11-display error when message mentions display.
  - Prints a generic windowing initialization error otherwise.
  - Exits with status `1`.
- Dispatches:
  - `--node-config` / `-N`: `ocfs2interface.nodeconfig.node_config()`
  - default: `ocfs2interface.console.main()`

Notable details:
- Uses Python 2 exception syntax and print redirection.
- Explicitly handles an old PyGTK behavior where missing `DISPLAY` was only a warning.
