<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/pyerrors.h -->
# sources/user-network-fs/samba/source4/libcli/util/pyerrors.h

Purpose: centralizes Python exception conversion macros for Samba C extension code using WERROR, HRESULT, NTSTATUS, and plain strings.

Important APIs and types: `PyErr_FromWERROR`, `PyErr_FromHRESULT`, `PyErr_FromNTSTATUS`, `PyErr_FromString`, `PyErr_SetWERROR`, `PyErr_SetHRESULT`, `PyErr_SetNTSTATUS`, `_and_string` variants, `PyErr_NTSTATUS_IS_ERR_RAISE`, `PyErr_NTSTATUS_NOT_OK_RAISE`, and `PyErr_WERROR_NOT_OK_RAISE`.

Control flow: each setter imports the `samba` Python module, fetches the named exception class, builds a tuple payload of numeric code and message, sets the Python error, and lets callers return NULL through convenience macros.

State and persistence: no local state is stored. The observable effect is Python interpreter exception state. The macros allocate Python objects but do not visibly decref imported module/class temporaries, relying on short-lived extension error paths.

Risks: repeated `PyImport_ImportModule` and `PyObject_GetAttrString` inside macros can leak references or mask import errors. Macros evaluate arguments in C macro context and should not receive expressions with side effects. Test signals include extension-level error conversion for all three status families, custom string overrides, and behavior when importing `samba` fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/pyerrors.h -->
