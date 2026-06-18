# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCompiler.hh

## Purpose
Provides a small compiler-portability macro for marking return values as important.

## Important APIs, Types, And Functions
Defines `XRD_WARN_UNUSED_RESULT` as `__attribute__((warn_unused_result))` for GCC and Clang, and as empty for other compilers.

## Control Flow
No runtime control flow. The macro affects compile-time diagnostics when attached to function declarations.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
No includes. It is intended for portable header use across XRootD modules.

## Risks And Test Signals
Risks are compiler-feature drift and inconsistent warnings on non-GNU compilers. Test signals are build logs confirming annotated APIs warn when ignored under GCC/Clang and compile cleanly elsewhere.
