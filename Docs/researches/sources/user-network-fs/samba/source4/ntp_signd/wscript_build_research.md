# sources/user-network-fs/samba/source4/ntp_signd/wscript_build

## Purpose

`source4/ntp_signd/wscript_build` declares the Samba service module for the NTP signing daemon.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_MODULE()` to build `service_ntp_signd` from `ntp_signd.c`, in subsystem `service`, with init function `server_service_ntp_signd_init`.

## Control Flow

At build time, the target is emitted only when `bld.AD_DC_BUILD_IS_ENABLED()` is true. Runtime service registration is delegated to the init function in `ntp_signd.c`.

## State and Persistence Behavior

The script only persists build metadata. It controls whether the NTP signing service is part of the AD DC build graph and which libraries it links against.

## Dependencies and Integration Points

Dependencies are `samdb`, `NDR_NTP_SIGND`, `LIBTSOCKET`, `LIBSAMBA_TSOCKET`, `GNUTLS_HELPERS`, and `samdb-common`. The module is non-internal so the service framework can load/register it.

## Risks and Edge Cases

Build coverage is AD-DC gated. Missing or misordered dependencies would surface as link failures for SAMDB, generated NDR, tstream, or GnuTLS hash helpers.

## Test Signals

Signals include successful AD DC build, service module load, and startup of `ntp_signd` with generated `server_service_ntp_signd_init` symbol resolved.
