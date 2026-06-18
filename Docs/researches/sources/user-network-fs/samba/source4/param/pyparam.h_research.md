# sources/user-network-fs/samba/source4/param/pyparam.h

Purpose: `pyparam.h` declares helper functions for converting Python loadparm-related inputs into C `struct loadparm_context` pointers.

Important APIs, types, and functions: It declares `_PUBLIC_ struct loadparm_context *lpcfg_from_py_object(TALLOC_CTX *, PyObject *)` and `_PUBLIC_ struct loadparm_context *py_default_loadparm_context(TALLOC_CTX *)`.

Control flow: Implementations in `pyparam_util.c` accept a Python string path, `None`, or a `samba.param.LoadParm` object and return a C loadparm context.

State and persistence behavior: Returned contexts may be global or talloc references to Python-backed contexts. The header itself has no state.

Dependencies and integration points: It includes `param/param.h` and uses Python object types. It is used by provisioning and Python xattr TDB helpers.

Risks: Callers need to know whether they receive a global context, a new loaded context, or a referenced Python object. Python headers must be included before or through compatible wrappers in translation units.

Test signals: Compile tests and Python/C bridge tests should verify conversions for string, `None`, valid LoadParm, and invalid object inputs.
