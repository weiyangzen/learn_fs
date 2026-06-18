<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.h -->
# sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.h

Purpose: public declaration for the GENSEC-backed `tstream_context` constructor. It keeps callers insulated from the implementation in `gensec_tstream.c` while preserving Samba's location-tracking allocation pattern.

Important APIs and types: forward-declares `struct gensec_context` and `struct tstream_context`, then declares `_gensec_create_tstream(TALLOC_CTX *, struct gensec_security *, struct tstream_context *, struct tstream_context **, const char *location)`. The macro `gensec_create_tstream()` supplies `__location__` automatically so allocation/debug traces identify the call site.

Control flow and state: the header has no runtime state, but its API contract implies the caller provides an already-negotiated GENSEC security object and a live plain tstream. The output pointer receives a wrapper stream that shares or references the lower stream rather than taking over all disconnect responsibility.

Dependencies and integration: consumed by authentication and protocol code that converts a negotiated GENSEC exchange into stream protection. It requires the including translation unit to have `NTSTATUS`, `TALLOC_CTX`, and `struct gensec_security` visible through Samba auth headers.

Risks and test signals: ABI consumers depend on the macro and symbol name. Header tests are build-level: include it from C files with minimal prerequisites, verify autoproto/export visibility, and ensure callers pass a mechanism with sign or seal negotiated because the implementation rejects otherwise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/gensec_tstream.h -->
