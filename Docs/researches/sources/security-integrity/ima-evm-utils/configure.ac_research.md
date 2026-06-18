# sources/security-integrity/ima-evm-utils/configure.ac

## Purpose
Autoconf configuration for ima-evm-utils. It defines package metadata, compiler checks, library/header probes, feature toggles, generated files, and a configuration summary.

## Important APIs, Types, And Functions
- `AC_INIT`, `AM_INIT_AUTOMAKE`, `AC_CONFIG_HEADERS`, `AC_CONFIG_MACRO_DIR`, and `LT_INIT` bootstrap the build.
- `PKG_CHECK_MODULES(LIBCRYPTO)` requires libcrypto >= 0.9.8.
- `AC_CHECK_LIB` and `AC_CHECK_HEADER` probe tpm2-tss, IBM TSS, OpenSSL engine/provider, xattr, and keyutils support.
- `AC_ARG_WITH(kernel_headers)` and `AC_ARG_ENABLE` define kernel headers, openssl config, sigv1, engine, provider, and kerneltests options.
- `AC_CONFIG_FILES` emits Makefiles and RPM spec.

## Control Flow
Configure checks programs and dependencies, sets Automake conditionals for optional components, applies debug or optimized CFLAGS, expands project-specific macros for docbook XSL and default hash algorithm, writes configured files, then prints a human-readable feature summary.

## State And Persistence
Persistent generated state includes `config.h`, Makefiles, configured spec file, and substituted variables such as `KERNEL_HEADERS` and `HASH_ALGO`.

## Dependencies And Integration Points
Depends on local m4 macros (`PKG_ARG_ENABLE`, `EVMCTL_MANPAGE_DOCBOOK_XSL`, `AX_DEFAULT_HASH_ALGO`), pkg-config, OpenSSL, keyutils, xattr headers, and optional TSS libraries.

## Risks And Edge Cases
A typo in the provider help text says `providre`. Optional engine/provider support depends on both symbols and headers, so OpenSSL version differences change build shape.

## Test Signals
Signals are configure success, correct conditional Makefile generation, and an accurate final summary of detected features.
