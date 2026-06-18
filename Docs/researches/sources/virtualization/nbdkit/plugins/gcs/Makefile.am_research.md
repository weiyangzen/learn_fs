# File Research: sources/virtualization/nbdkit/plugins/gcs/Makefile.am

This Automake file installs the Python Google Cloud Storage plugin script.

Key behavior:
- Distributes `gcs.py`, `nbdkit.py`, and the plugin POD.
- When Python is available, creates executable `nbdkit-gcs-plugin` by substituting `@sbindir@` in `gcs.py`.
- Installs the generated script as a plugin script.
- If POD tooling is available, builds `nbdkit-gcs-plugin.1`.

Integration:
- The generated shebang points at the built or installed nbdkit Python runner.
- `nbdkit.py` is distributed for unit-test stubbing, not as the real in-process module.
