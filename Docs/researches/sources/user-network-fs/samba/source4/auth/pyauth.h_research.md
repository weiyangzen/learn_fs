<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.h -->
# sources/user-network-fs/samba/source4/auth/pyauth.h

Purpose: small Python-auth binding header exposing conversion helpers for `auth_session_info` Python objects.

Important APIs and types: includes pytalloc and `auth/session.h`, defines `PyAuthSession_AsSession(obj)` as a direct pytalloc extraction of `struct auth_session_info`, and declares `PyObject_AsSession(PyObject *obj)`.

Control flow and state: no runtime flow in the header. The macro assumes callers have already validated or are willing to receive NULL from pytalloc if the Python object does not wrap the expected type.

Dependencies and integration: used by C extension modules that need to accept or return Samba auth session objects. It ties Python bindings to the native `auth_session_info` layout.

Risks and test signals: because the macro does not raise Python exceptions itself, callers must perform type checks and error reporting. Build tests should ensure C files including this header have Python and pytalloc types visible. Python binding tests should exercise invalid object conversion through functions that use `PyObject_AsSession()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.h -->
