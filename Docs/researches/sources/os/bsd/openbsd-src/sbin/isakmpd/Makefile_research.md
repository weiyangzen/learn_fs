# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/Makefile

This is the OpenBSD build file for the `isakmpd` daemon.

Key responsibilities:
- Defines `PROG=isakmpd`.
- Lists core source files for ISAKMP/IKE, IPsec DOI, PF_KEY, policy, monitor, NAT traversal, transport, crypto, UI, and utility support.
- Adds `.PATH` for OpenBSD-specific system-dependent sources.
- Defines generated constant/field headers and sources.
- Invokes `genconstants.sh` and `genfields.sh` to generate `exchange_num`, `ipsec_num`, `isakmp_num`, `ipsec_fld`, and `isakmp_fld` artifacts.
- Installs manual pages `isakmpd.8`, `isakmpd.conf.5`, and `isakmpd.policy.5`.
- Sets warning flags and include paths.
- Links against KeyNote, crypto, math, and optional LWRES DNSSEC library.
- Includes commented options for debugging and DNSSEC support.
- Ensures generated files are built first with `BUILDFIRST`.

Dependencies:
- OpenBSD `bsd.prog.mk`.
- Local generator scripts and `.cst`/`.fld` metadata files.
- Libraries: `libkeynote`, `libcrypto`, `libm`, and optionally `liblwres`.

Research notes:
- `dnssec.c` is present in the tree but not included by default unless DNSSEC support is enabled.
- The build relies on generated protocol constants and field accessor code.
