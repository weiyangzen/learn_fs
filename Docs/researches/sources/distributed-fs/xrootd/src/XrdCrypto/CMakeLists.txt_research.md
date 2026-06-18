# sources/distributed-fs/xrootd/src/XrdCrypto/CMakeLists.txt

## Purpose

This CMake file defines how XRootD crypto components are built and installed. It separates low-level utility-linked crypto objects, a lightweight OpenSSL-dependent crypto library, the abstract `XrdCrypto` facade library, and the OpenSSL implementation plugin.

## Important APIs and Targets

`target_sources(XrdUtils PRIVATE ...)` adds base X.509/RSA/auxiliary and OpenSSL concrete utility sources to `XrdUtils` to avoid linking all of `libXrdCryptossl` into utility users. `XrdCryptoLite` is a shared library built from `XrdCryptoLite.cc`, `XrdCryptoLite.hh`, and `XrdCryptoLite_bf32.cc`, linked to `XrdUtils` and `OpenSSL::Crypto`. `XrdCrypto` is a shared abstract facade built from basic/cipher/factory/digest/GSI-chain sources. `${XrdCryptossl}` is a module plugin named `XrdCryptossl-${PLUGIN_VERSION}`.

## Control Flow

Configure-time flow declares sources, links dependencies, sets `SOVERSION`/`VERSION`, adds the plugin to the aggregate `plugins` target, and installs all three library/module targets under `${CMAKE_INSTALL_LIBDIR}`.

## State and Persistence Behavior

Build state is target-level. Installed artifacts persist ABI boundaries: `XrdCrypto` and `XrdCryptoLite` are shared libraries while the OpenSSL implementation is a loadable module.

## Dependencies and Integration Points

Targets integrate with `XrdUtils`, OpenSSL crypto/SSL imported targets, CMake thread libs, dynamic-loader libs, and the repository's plugin versioning scheme.

## Risks and Edge Cases

Moving concrete OpenSSL sources into `XrdUtils` widens what utility consumers compile/link, so symbol/ABI changes there have broad impact. Plugin naming must match runtime factory loader expectations (`libXrdCrypto<factory>.so`). OpenSSL provider behavior affects `XrdCryptoLite_bf32`.

## Test Signals

Build tests should verify all targets link, install names match runtime loader names, `plugins` depends on the SSL module, and consumers can load `XrdCryptossl` through `XrdCryptoFactory`.
