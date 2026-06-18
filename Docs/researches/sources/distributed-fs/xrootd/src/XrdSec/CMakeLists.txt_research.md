# sources/distributed-fs/xrootd/src/XrdSec/CMakeLists.txt

## Purpose

This CMake fragment builds XRootD security support into `XrdUtils` and creates the loadable security plugin modules.

## Important APIs, Types, And Functions

- Defines module target names `XrdSec-${PLUGIN_VERSION}` and `XrdSecProt-${PLUGIN_VERSION}`.
- Adds entity, attribute, extra, load-security, and monitor sources to `XrdUtils`.
- Builds `${XrdSec}` module from client/server protocol manager, interfaces, trace, entity pin, and transport-layer sources.
- Builds `${XrdSecProt}` module from protector sources.
- Links `${XrdSec}` to `XrdUtils`; links `${XrdSecProt}` to `XrdUtils` and `OpenSSL::Crypto`.
- Adds both modules to the `plugins` dependency target and installs them.

## Control Flow

CMake compiles base entity support into the utility library and plugin-facing security protocol machinery into modules. Install rules place module shared libraries in the configured library directory.

## State And Persistence

Build outputs are the two plugin modules plus `XrdUtils` object content. No runtime state is in the CMake file.

## Dependencies And Integration Points

It depends on parent targets `XrdUtils`, `plugins`, `OpenSSL::Crypto`, and `${PLUGIN_VERSION}`. It is foundational for security protocol loading and for other modules such as SciTokens that include `XrdSecEntity`.

## Risks And Edge Cases

- Splitting entity classes into `XrdUtils` means ABI changes affect many consumers.
- Module names are versioned; runtime config must reference the correct installed names or symlinks.
- Missing source additions here can cause runtime plugin symbols to be absent.

## Test Signals

Build tests should verify both modules are produced and installed. Runtime tests should load security protocols and confirm `XrdSecGetProtocol` resolves from the module.
