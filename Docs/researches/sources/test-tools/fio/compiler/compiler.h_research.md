## sources/test-tools/fio/compiler/compiler.h

Purpose: centralizes compiler attributes and compile-time helper macros used throughout fio.

Important APIs and flow: defines `__must_check`, compile-time warning/error attributes, `fio_unused`, constructor/destructor markers `fio_init`/`fio_exit`, `fio_unlikely`, `typecheck()`, `compiletime_assert()` variants, `FIO_ARRAY_SIZE`, `FIO_FIELD_SIZE`, and portable `fio_fallthrough`.

State and persistence: no runtime state. Constructor/destructor attributes affect process initialization order for modules such as cgroup and client hash setup.

Dependencies and integration: depends on compiler support detected by `configure`, especially `CONFIG_STATIC_ASSERT`, `CONFIG_DISABLE_OPTIMIZATIONS`, and `__has_attribute`. It is included by low-level utility code such as `murmur3.c`.

Risks and test signals: compiler feature differences can change whether assertions are enforced. The fallback compile-time assertion path relies on optimizer behavior unless `_Static_assert` is available. Build coverage across GCC/Clang and optimized/unoptimized configurations is the key signal.
