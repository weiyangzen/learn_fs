# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindKrb5.cmake

Purpose: Finds Kerberos 5 and requested krb5-config components, producing include directories and ordered libraries for RPCSEC_GSS/GSSAPI-related builds.

Important APIs/types/functions: Consumes `KRB5_PREFIX` and `KRB5_FIND_COMPONENTS`; finds `krb5-config`, runs it for `--cflags` and `--libs`, parses `-I`, `-L`, and `-l` flags, appends `gssapi_krb5`, finds each library, and sets `KRB5_FOUND`, `KRB5_INCLUDE_DIRS`, and `KRB5_LIBRARIES`.

Control flow: If `krb5-config` is missing, marks not found. If present, command execution results must be zero before include/library parsing proceeds. Each parsed library is resolved with hinted and default searches; any missing library clears found state. Final status or fatal messaging depends on find options.

State and persistence behavior: CMake cache/library variables only.

Dependencies and integration points: Security/authentication build paths consume Kerberos headers and libraries, especially GSSAPI.

Risks: It unconditionally prepends `"${KRB5_PREFIX}/include"` even when prefix is unset. It always appends `gssapi_krb5`, which may be MIT-specific and wrong for Heimdal. Existing `KRB5_LIBRARIES` is not cleared before accumulation in repeated configure scenarios.

Test signals: Configure with MIT Kerberos, Heimdal, custom prefix, component lists such as `gssapi`, missing `krb5-config`, and repeated reconfigure after changing prefix.
