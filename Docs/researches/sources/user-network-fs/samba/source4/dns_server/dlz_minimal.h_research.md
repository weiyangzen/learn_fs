# sources/user-network-fs/samba/source4/dns_server/dlz_minimal.h

## Purpose
Provides a local minimal copy of the BIND DLZ dlopen ABI needed to compile Samba's DLZ module across supported BIND versions.

## Important APIs, types, and functions
- Version gates define `DLZ_DLOPEN_VERSION`, `DNS_CLIENTINFO_VERSION`, and `ISC_BOOLEAN_AS_BOOL` for BIND 9.10, 9.11, 9.12, 9.14, 9.16, and 9.18.
- Defines `isc_result_t`, `isc_boolean_t`, `dns_ttl_t`, result codes, boolean constants, log levels, and opaque BIND handle types.
- Defines `dns_clientinfo_t` and `dns_clientinfomethods_t` differently for client-info ABI v1 and v2.
- Declares callback types `log_t`, `dns_sdlz_putrr_t`, `dns_sdlz_putnamedrr_t`, and `dns_dlz_writeablezone_t`.
- Declares the DLZ entry point prototypes implemented by `dlz_bind9.c`.

## Control flow
Compile-time preprocessor selection rejects unsupported BIND versions and old 9.8/9.9 versions. There is no runtime control flow.

## State and persistence behavior
No state or persistence. The header fixes ABI constants and type signatures used when BIND loads the Samba module.

## Dependencies and integration points
Includes standard integer/bool headers and expects the build system to define exactly one supported `BIND_VERSION_*` macro. It is tightly coupled to BIND's external DLZ ABI and to `dlz_bind9.c`.

## Risks and edge cases
- New BIND versions fail compilation until explicitly added.
- ABI drift in BIND can break the copied definitions.
- `isc_boolean_t` changes between `int` and `bool` depending on version, which affects function signatures and binary compatibility.

## Test signals
Build matrix coverage against every supported BIND version is the main signal. Runtime smoke tests should load the module into each BIND version and exercise lookup and dynamic update entry points.
