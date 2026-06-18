# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/config.h

Generated Unbound `config.h` for the OpenBSD `unwind` embedded Unbound build. It captures platform capabilities, feature toggles, package metadata, compatibility shims, and default paths.

Key configuration:
- Package version: `unbound 1.25.1`.
- Configure line enables all symbols, OpenSSL/LibreSSL, libevent, expat; disables Python module, shared libraries, explicit port randomisation, and pthreads.
- Default paths point to `/var/unbound`.
- `HAVE_LIBRESSL`, `HAVE_SSL`, `USE_LIBEVENT`, `USE_ECDSA`, `USE_ED25519`, `USE_SHA1`, and `USE_SHA2` are enabled.
- `USE_DNSTAP`, `USE_DNSCRYPT`, `USE_CACHEDB`, `USE_DSA`, `USE_GOST`, `USE_IPSECMOD`, `USE_IPSET`, Python bindings, and Windows support are disabled.
- `DISABLE_EXPLICIT_PORT_RANDOMISATION` is enabled for kernel-based UDP source port randomization.

Compatibility layer:
- Provides replacement symbol mappings for absent functions such as `inet_pton`, `inet_ntop`, `strlcpy`, `strlcat`, `reallocarray`, `explicit_bzero`, and others when needed.
- Defines attribute macros like `ATTR_FORMAT`, `ATTR_UNUSED`, `ATTR_NONSTRING`, and fallthrough/noreturn helpers.
- Enables extension macros such as `_OPENBSD_SOURCE`, `_NETBSD_SOURCE`, `_GNU_SOURCE`, etc.
- Defines Unbound default ports for DNS, DoT, DoH, DoQ, and control.

Role in group:
- Central compile-time contract for all embedded Unbound files in this group.
