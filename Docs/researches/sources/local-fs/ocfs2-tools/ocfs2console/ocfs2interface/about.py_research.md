# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/about.py

Command-line argument handling and About dialog for OCFS2 Console.

Key functions:
- `print_version()`
  - Prints `OCFS2Console version <OCFS2TOOLS_VERSION>`.
- `print_usage(name)`
  - Documents `--node-config`, `--version`, and `--help`.
- `process_args()`
  - Parses top-level args.
  - Returns whether node-config-only mode was requested.
  - Exits for version/help.
- `process_gui_args()`
  - Allows only no args or `--clusterconf` / `-C`.
- `about(parent)`
  - For PyGTK >= 2.6, uses `gtk.AboutDialog`.
  - For older PyGTK, falls back to `gtk.MessageDialog`.
- `main()`
  - Processes args and shows About dialog.

Dependencies:
- `confdefs.OCFS2TOOLS_VERSION`
- `guiutil.set_props`
- `gtk`

Notable details:
- `--clusterconf` is accepted by GUI arg validation but not otherwise handled in this file.
