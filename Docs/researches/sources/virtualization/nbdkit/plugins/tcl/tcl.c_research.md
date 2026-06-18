# File Research: sources/virtualization/nbdkit/plugins/tcl/tcl.c

Implements the `tcl` nbdkit plugin, a bridge that loads a Tcl script and delegates nbdkit callbacks to Tcl procedures.

Key behavior:
- `.load` creates one global `Tcl_Interp` and initializes Tcl.
- `.unload` deletes the interpreter and calls `Tcl_Finalize`.
- The first config parameter must be `script=/path/to/script.tcl`. The plugin evaluates that file and requires Tcl procs `plugin_open`, `get_size`, and `pread`.
- Later config parameters are passed to the script’s optional `config` proc; if absent, unknown configuration is rejected like a C plugin with no config callback.
- Optional script procs include `dump_plugin`, `config_complete`, `plugin_close`, `pwrite`, `can_write`, `can_flush`, `can_trim`, `zero`, `is_rotational`, `plugin_flush`, and `trim`.
- `.open` calls `plugin_open readonly` and stores the Tcl object result as the nbdkit handle with an incremented reference count.
- `.close` optionally calls `plugin_close handle`, then decrements the handle object refcount.
- `.get_size` calls `get_size handle` and converts the Tcl result to `Tcl_WideInt`.
- `.pread` calls `pread handle count offset`, expects a byte array at least `count` bytes, and copies it into nbdkit’s buffer.
- `.pwrite` passes a Tcl byte array and offset to optional `pwrite`; without it, writes fail.
- Capability callbacks either call explicit Tcl capability procs or infer support from the presence of data callbacks, matching nbdkit C-plugin defaults.
- `.zero` returns `EOPNOTSUPP` when no Tcl `zero` proc exists, allowing fallback to pwrite.
- Thread model is `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`, protecting the single Tcl interpreter from concurrent use.

Dependencies:
- Tcl C API.
- nbdkit plugin API.

Notes and risks:
- `Tcl_GetBooleanFromObj` return values are not checked in capability callbacks; malformed Tcl boolean results may leave `r` as the previous evaluation status.
- The Tcl interpreter is global, so script state is shared across all clients.
- The bridge intentionally serializes all requests, prioritizing interpreter safety over parallelism.
