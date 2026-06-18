## sources/distributed-fs/xrootd/src/XrdSys/CMakeLists.txt

Purpose: attaches the XrdSys implementation and public/private support headers to the `XrdUtils` target.

Important APIs/types/functions: uses `target_sources(XrdUtils PRIVATE ...)` to include atomics, directory wrappers, error translation, extended attributes, CLOEXEC FD helpers, fallocate compatibility, IO event pollers, logging, platform portability, plugin loading, privilege/thread/timer/trace/util/xattr/lock helpers, and platform-specific `.icc` implementations.

Control flow: CMake configuration does not contain conditional logic here; platform selection happens inside source files with preprocessor directives. This list is the build integration point that ensures inline `.icc` files and headers are visible to the target source graph.

State and persistence: no runtime state. Its persistent effect is build graph membership for `XrdUtils`.

Dependencies and integration: integrates the XrdSys module into the larger XRootD build. The listed files expose utility services used by higher-level Xrd, XrdCl, XrdOss, and authentication code.

Risks: missing a `.cc`, `.hh`, or `.icc` here can cause unresolved symbols or platform-specific missing code. Adding headers as private sources helps IDE visibility but does not install them by itself.

Test signals: configure and build on Linux, macOS, BSD/Solaris where applicable; verify `XrdUtils` exports expected symbols and that platform-specific `.icc` selections compile.
