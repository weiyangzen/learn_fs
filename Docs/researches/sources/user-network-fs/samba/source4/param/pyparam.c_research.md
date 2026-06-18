# sources/user-network-fs/samba/source4/param/pyparam.c

Purpose: `pyparam.c` implements the `samba.param` Python extension exposing Samba loadparm configuration objects and compiled path helpers.

Important APIs, types, and functions: It defines Python types `param.LoadParm` and `param.LoadparmService`, helpers `py_lp_ctx_get_helper`, load/set/dump/path/server-role methods, mapping access by service name, `py_lp_ctx_new`, and module functions `data_dir`, `default_path`, `setup_dir`, `modules_dir`, `bin_dir`, and `sbin_dir`.

Control flow: `LoadParm()` returns a reference to the global loadparm context by default, or loads a non-global config when `filename_for_non_global_lp` is supplied. Methods call loadparm getters/setters and convert parameter types to Python bool/int/string/list. Parametric options are parsed by `type:option` syntax for global or service scope. Dump methods write to stdout or opened files.

State and persistence behavior: The default Python object references Samba's global loadparm context, so changes can be process-wide. Non-global construction creates a separate context. Dump methods persist config text to requested files; path helpers return configured filesystem paths.

Dependencies and integration points: It depends on Python C API, pytalloc, Samba hostconfig/loadparm APIs, dynconfig constants, debug level access, and server role helpers. `pyparam_util.c` consumes the exposed `LoadParm` type.

Risks: Shared global context behavior can surprise Python callers. File dump methods open arbitrary paths/modes supplied by Python. Parameter conversion must stay in sync with loadparm enum/type definitions. Some error paths return NULL without setting a detailed Python exception.

Test signals: Python tests should cover global versus non-global construction, parametric get/set, service mapping, dump file output, compiled directory functions, weak_crypto property, server-role reporting, and unknown parameter/service errors.
