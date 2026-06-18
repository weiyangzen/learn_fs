# File Research: sources/virtualization/nbdkit/plugins/python/plugin.h

Shared header for the Python plugin implementation. It fixes `NBDKIT_API_VERSION` at 2, includes `nbdkit-plugin.h`, and defines `ACQUIRE_PYTHON_GIL_FOR_CURRENT_SCOPE`, a cleanup-based helper that uses `PyGILState_Ensure`/`PyGILState_Release` around callbacks.

Declares global plugin state (`script`, imported `module`, selected `py_api_version`, thread-local `last_error`) plus helper APIs from companion source files: callback lookup, Python string conversion, Python exception checking, and built-in `nbdkit` module creation.
