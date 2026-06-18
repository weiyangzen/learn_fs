<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.h -->
# sources/user-network-fs/libsmb2/lib/spnego-wrapper.h

Purpose: Declares the private SPNEGO wrapper interface used by libsmb2 authentication code.

Important APIs, types, and functions: Exports `SPNEGO_MECHANISM_KRB5` and `SPNEGO_MECHANISM_NTLMSSP` bit flags plus prototypes for negotiate, NTLMSSP challenge/auth wrapping, authenticate result wrapping, and GSS/SPNEGO blob unwrapping.

Control flow: Header-only declaration layer; callers include it and invoke the C implementation based on whether they need to produce a SPNEGO token or parse one from a server/client.

State and persistence behavior: No runtime state. It establishes the ownership contract implicitly: wrapper outputs are returned through `void **`, parser outputs point into input buffers.

Dependencies and integration points: Depends on `struct smb2_context`, `uint8_t`, and `uint32_t` from surrounding libsmb2 headers. Integrated by session setup and authentication implementation files.

Risks: The include guard is misspelled `SPEGNO_WRAPPER_H`, which is harmless but easy to propagate. Lack of explicit ownership comments can cause leaks or invalid frees by new callers.

Test signals: Compile coverage when SPNEGO implementation is built; no direct header-specific test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.h -->
