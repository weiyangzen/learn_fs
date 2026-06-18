# sources/distributed-fs/xrootd/src/XrdOssArc/CMakeLists.txt

Purpose: controls whether and how the `XrdOssArc` archive storage-system plug-in is built and installed.

Important APIs/types/functions: CMake option gate `BUILD_XRDOSSARC`, module target `XrdOssArc-${PLUGIN_VERSION}`, source list for archive wrapper, backup, compose, config, directory, file, FS monitor, stage, stop monitor, trace, and zip-file code, and install rule to `${CMAKE_INSTALL_LIBDIR}`.

Control flow: if `BUILD_XRDOSSARC` is false, CMake returns immediately. Otherwise it creates a module library, links it privately with `XrdUtils`, `XrdServer`, `libzip::zip`, and thread libraries, then installs the module.

State and persistence behavior: build-system state only. It determines whether the runtime plug-in exists and which implementation files are compiled into it.

Dependencies: project variables `PLUGIN_VERSION`, `CMAKE_THREAD_LIBS_INIT`, install dirs, and imported `libzip::zip`.

Integration points: this is the build entry for the OSS archive overlay loaded by XRootD. Missing files here mean corresponding wrapper, backup, staging, or zip behavior is unavailable at runtime.

Risks: builds without `BUILD_XRDOSSARC` hide compile errors; `libzip::zip` availability controls the module; header files in the source list help IDEs but do not enforce separate compilation.

Test signals: configure with flag on/off, link against libzip and server libraries, install packaging checks, and module-load smoke test through `osslib`/pushed OSS configuration.
