# sources/user-network-fs/samba/source4/dns_server/wscript_build

## Purpose
`wscript_build` defines how Samba builds the DNS server components, BIND DLZ modules, shared DNS common library, and Python DNS bindings. It encodes which pieces are AD-DC-only and which remain available for client-side tooling.

## Important APIs, Types, and Functions
- `bld.SAMBA_LIBRARY('dnsserver_common', ...)` builds the shared common helper library independently of AD DC enablement.
- `bld.SAMBA_MODULE('service_dns', ...)` builds the internal DNS service module from server, query, update, utility, and crypto sources.
- `bld.SAMBA_LIBRARY('dlz_bind9_*', ...)` builds version-specific BIND DLZ modules for 9.10, 9.11, 9.12, 9.14, 9.16, and 9.18 plus a torture variant.
- `bld.SAMBA_PYTHON('python_dsdb_dns', ...)` builds `samba/dsdb_dns.so` from `pydns.c`.

## Control Flow
This build script is declarative. `dnsserver_common` is always declared as a private library so imports and tools can work even when AD DC support was not built. The internal DNS service and DLZ modules are gated by `bld.AD_DC_BUILD_IS_ENABLED()`. Python utility library names are discovered through `bld.pyembed_libname()` before building the Python extension.

## State and Persistence
No runtime state is persisted here. Build outputs include private libraries, service modules, installed BIND module `.so` files, and the Python extension.

## Dependencies and Integration Points
Dependencies tie DNS code into `samba-hostconfig`, `LIBTSOCKET`, `LIBSAMBA_TSOCKET`, `ldbsamba`, `clidns`, `gensec`, `auth`, `samba_server_gensec`, `samdb-common`, `popt`, and Python embedding utilities. DLZ modules install under `${MODULESDIR}/bind9`.

## Risks and Edge Cases
- New BIND versions require adding another near-duplicate `dlz_bind9_*` target.
- `dnsserver_common` intentionally has a wider build surface than service DNS; dependency additions there should not accidentally require AD DC-only libraries.
- Service DNS is `internal_module=False`, so packaging/module installation assumptions matter.

## Test Signals
Build tests should cover AD DC enabled and disabled configurations, Python extension import without AD DC service build, all supported BIND DLZ target variants, and dependency changes that might break standalone tooling.
