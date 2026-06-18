# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt_config.h

Generated-style feature shim for DNSCrypt.

Behavior:
- Exists so code can check `USE_DNSCRYPT` without directly including full `config.h`.
- Contains `#if 0 /* ENABLE_DNSCRYPT */`, so it does not define `USE_DNSCRYPT`.

Role in group:
- Confirms DNSCrypt is disabled in this OpenBSD embedded Unbound build.
