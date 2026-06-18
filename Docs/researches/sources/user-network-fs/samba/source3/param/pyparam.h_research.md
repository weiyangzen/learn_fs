# sources/user-network-fs/samba/source3/param/pyparam.h

Purpose: small public header for converting Python objects into Samba loadparm contexts.

Important API: declares `_PUBLIC_ struct loadparm_context *lpcfg_from_py_object(TALLOC_CTX *mem_ctx, PyObject *py_obj);`. It includes `param/param.h`, relying on the Python object type being available through surrounding Python includes in consumers.

State and persistence: no state; it declares a conversion/adapter function implemented in `pyparam_util.c`.

Dependencies and integration: used by Python-facing Samba3 utilities that accept an optional `samba.param.LoadParm` object or `None` and need a C `loadparm_context`.

Risks: the header exposes `PyObject` without including Python headers itself, so include order matters. API consumers must honor talloc ownership of returned contexts/references.

Test signals: compile tests for Python extension consumers and runtime conversion of `None`, valid LoadParm, and invalid Python object inputs.
