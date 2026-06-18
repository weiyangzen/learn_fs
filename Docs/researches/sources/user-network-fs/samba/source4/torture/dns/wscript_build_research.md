# sources/user-network-fs/samba/source4/torture/dns/wscript_build Research

## Purpose
This Waf build fragment declares the DNS torture modules for Samba AD DC builds. It wires the BIND DLZ integration tests and internal DNS tests into the `smbtorture` subsystem.

## Important APIs, Types, And Functions
The script is guarded by `bld.AD_DC_BUILD_IS_ENABLED()`. It calls `bld.SAMBA_MODULE()` for `TORTURE_BIND_DNS` and `TORTURE_INTERNAL_DNS`. `TORTURE_BIND_DNS` uses `dlz_bind9.c`, initializes through `torture_bind_dns_init`, defines `BIND_VERSION_9_16`, and depends on `torture`, `talloc`, `torturemain`, and `dlz_bind9_for_torture`. `TORTURE_INTERNAL_DNS` uses `internal_dns.c`, initializes through `torture_internal_dns_init`, and depends on `torture`, `talloc`, and `torturemain`.

## Control Flow
There is no runtime control flow. At build time, AD DC support decides whether either module is declared. If enabled, both are internal smbtorture modules and become available through their init functions.

## State And Persistence
The file affects build graph state only. Its persistent effect is the compiled module set included in an AD DC capable build.

## Dependencies And Integration Points
This fragment integrates with Samba's Waf build system and smbtorture. The BIND DLZ test depends on `dlz_bind9_for_torture`, while `-DBIND_VERSION_9_16` couples compilation to the expected BIND9 API.

## Risks And Test Signals
The key signal is successful build and registration when AD DC is enabled. Risks include stale BIND version flags, missing DLZ torture dependency, or absent DNS torture coverage in non-AD-DC builds.
