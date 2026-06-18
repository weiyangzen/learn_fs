# sources/user-network-fs/libtirpc/src/xdr_sizeof.c

Purpose: `xdr_sizeof.c` estimates how many bytes an object will occupy when XDR-encoded, without writing to a real output stream.

Important APIs, types, and functions: Public `xdr_sizeof` installs a synthetic encode-only `xdr_ops` table. `x_putlong` adds four bytes, `x_putbytes` adds the byte count, `x_inline` tracks inline byte requests and allocates scratch storage when needed, `x_getpostn` returns the accumulated count, and `x_destroy` frees scratch state.

Control flow: `xdr_sizeof` initializes an `XDR` in `XDR_ENCODE`, points it at synthetic ops, invokes the caller's XDR function, frees any scratch inline allocation, and returns the accumulated size on success or zero on failure. Decode-oriented operations are mapped to a harmless false-return function.

State and persistence behavior: State lives in the stack `XDR` object plus optional heap scratch used to satisfy inline encode requests. No caller data is modified except whatever side effects the supplied XDR function has during encode.

Dependencies and integration points: It depends on `rpc/xdr.h` and is used by callers that need buffer sizing before encoding variable RPC payloads or auth-protected data.

Risks: This is an estimate driven by encode paths; XDR functions with side effects, operation-sensitive behavior, or unsupported set-position requirements may report zero or inaccurate sizes. `x_inline` uses `x_base` as a stored allocation length cast through a pointer, which is clever but non-obvious. The returned type is `unsigned long`, but failure returns indistinguishable zero from a genuinely zero-sized encoding.

Test signals: Tests should compare `xdr_sizeof` against actual `xdrmem_create` encodings for scalars, strings, arrays, inline-heavy generated code, and failure cases.
