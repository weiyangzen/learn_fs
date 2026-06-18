
## sources/storage-engines/wiredtiger/ext/compressors/iaa/CMakeLists.txt

Purpose: defines the WiredTiger IAA compression extension build. It exposes `HAVE_BUILTIN_EXTENSION_IAA` as a CMake boolean gated on `HAVE_LIBQPL`, rejects simultaneous builtin and dynamically loaded builds, builds the C++ `iaacodec` helper library when either IAA mode is enabled, then builds `wiredtiger_iaa` as an `OBJECT` target for builtin use or `MODULE` target for runtime extension loading.

Important APIs and integration: the target consumes WiredTiger generated headers, `src/include`, `iaacodec/include`, and Intel QPL via `wt::qpl`. Dynamic `ENABLE_IAA` builds install the module and link `CMAKE_DL_LIBS`; if libaccel-config is present it also links `wt::accel_config`. The static codec target is PIC so it can be embedded into the module or builtin extension.

State and persistence: no runtime state; it controls whether the persistent compression format can be produced/read by linking in `iaa_compress.c` and the C++ QPL bridge. Risks: build mode exclusivity is explicit, but QPL and optional accelerator configuration availability are external. Test signals include configuring both modes to assert the fatal path, configuring without QPL to assert dependency errors, and running extension compression tests on hardware and software fallback hosts.
