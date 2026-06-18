# sources/user-network-fs/samba/source3/param/pyparam.c

Purpose: implements the `samba.samba3.param` Python extension module and exposes a `get_context()` method returning an S3-backed `samba.param.LoadParm` object.

Important APIs and flow: `py_get_context()` obtains `loadparm_s3_helpers()`, calls `loadparm_init_s3()` on a stackframe, then transfers the resulting context to Python with `pytalloc_steal(loadparm_Type, ...)`. `MODULE_INIT_FUNC(param)` creates the module, imports `samba.param`, looks up the `LoadParm` Python type, and stores it in static `loadparm_Type`.

State and persistence: only module-global `loadparm_Type` is stored. The returned context is memory-managed through pytalloc after ownership transfer.

Dependencies and integration: uses Python C API compatibility wrappers, `pytalloc`, `param/loadparm.h`, and shared Samba Python module `samba.param`. Build integration is in `param/wscript_build` as `pys3param`.

Risks: initialization failure paths after `PyImport_ImportModule()` return `NULL` without DECREFing the already created module object, but import-time failure usually aborts module loading. Correctness depends on `samba.param.LoadParm` matching the talloc-wrapped `struct loadparm_context` type.

Test signals: importing `samba.samba3.param`, calling `get_context()`, and using returned LoadParm APIs from Python with Python build enabled.
