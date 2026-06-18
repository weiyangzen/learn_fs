# sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdPlatform.hh

## Purpose
`XrdSecpwdPlatform.hh` isolates platform-specific declarations needed by the password protocol for `crypt()` and shadow password access. It keeps the main protocol source portable across Linux, GNU/Hurd-like, Solaris, macOS, OSF, SGI, and optional shadow-password configurations.

## Important APIs, types, and functions
The header conditionally includes `<crypt.h>` on platforms that provide it and declares `extern "C" char *crypt(const char *, const char *)` on platforms where the function may exist without that header. It always includes `<grp.h>` and includes `<shadow.h>` when `HAVE_SHADOWPW` is defined.

## Control flow
There is no runtime control flow. Preprocessor branches select the correct declarations at compile time based on platform macros and configure-time feature macros.

## State and persistence behavior
The header declares no state and performs no persistence. It enables `XrdSecProtocolpwd.cc` to call `crypt()` and, when available, `getspnam()` against system password databases.

## Dependencies and integration points
This file is included by `XrdSecProtocolpwd.cc`. Its declarations support `CheckCreds()` for crypt-style password comparison and `QueryCrypt()` for reading system shadow password hashes. It also connects the build-time `HAVE_SHADOWPW` feature check to the protocol's runtime behavior.

## Risks and edge cases
Platform detection must match the C library and compiler environment. Missing `crypt()` declarations can cause build failures or unsafe implicit declarations on older compilers. Shadow password support requires both headers and sufficient runtime privileges; the header only exposes the API, while `XrdSecProtocolpwd.cc` must still handle permission failures.

## Test signals
Build matrix coverage should include Linux/glibc with `<crypt.h>`, macOS-style explicit `crypt()` declaration, and configurations with and without `HAVE_SHADOWPW`. Runtime tests for the password protocol's crypt and shadow paths confirm that these declarations link correctly with `${CRYPT_LIBRARY}`.
