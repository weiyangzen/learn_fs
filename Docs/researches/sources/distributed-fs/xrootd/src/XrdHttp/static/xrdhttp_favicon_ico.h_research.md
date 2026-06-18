# sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_favicon_ico.h

Purpose: Embeds the XrdHTTP favicon asset as a C byte array.

Important APIs/types/functions: Defines `unsigned char favicon_ico[]` and `unsigned int favicon_ico_len`. The data begins with a GIF signature despite the `.ico` naming, so consumers should serve the bytes as the established favicon resource rather than infer strict ICO structure from the symbol name.

Control flow: No executable control flow. Static serving code writes the byte array to clients.

State and persistence: Compiled read-only asset data. No runtime state.

Dependencies and integration points: Included by `XrdHttpStatic.hh`; used by the HTTP static resource endpoint.

Risks: Header-defined globals can duplicate at link time if included broadly. MIME/type assumptions around favicon `.ico` versus embedded GIF bytes may matter for strict clients, though browsers are tolerant. Asset regeneration must keep `favicon_ico_len` synchronized.

Test signals: Request the favicon path, verify response body size and browser display, and run a full link build to catch duplicate symbols.
