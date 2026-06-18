# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap_config.h

Generated-style feature shim for dnstap.

Behavior:
- Exists so code can check `USE_DNSTAP` without directly including full `config.h`.
- Contains `#if 0 /* ENABLE_DNSTAP */`, so it does not define `USE_DNSTAP`.

Role in group:
- Confirms dnstap is disabled in this OpenBSD embedded Unbound build.
