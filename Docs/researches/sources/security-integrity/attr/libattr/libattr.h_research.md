## sources/security-integrity/attr/libattr/libattr.h

Purpose: forced internal feature header for libattr builds.

It defines `HAVE_ATTR_LIBATTR_H`, `HAVE_CONFIG_H`, and the xattr syscall feature macros so library sources compile desired code paths. State is compile-time only. Dependencies are inclusion through `-include libattr/libattr.h` in the build fragment. Risks are divergence from Autoconf probes and forcing code paths on unsupported platforms if misused. Test signal is successful Linux build and expected xattr-copy symbols.
