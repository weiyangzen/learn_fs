# sources/test-tools/liburing/test/version.c

Purpose: sanity test for liburing compile-time and runtime version APIs/macros.

Important APIs/types/functions: `io_uring_major_version`, `io_uring_minor_version`, `IO_URING_VERSION_MAJOR`, `IO_URING_VERSION_MINOR`, `IO_URING_CHECK_VERSION`, and `T_EXIT_PASS`/`T_EXIT_FAIL`.

Control flow: main first verifies that checking the runtime major/minor pair does not report a newer required version. It then requires runtime major and minor values to equal the compile-time version macros. Finally, it uses a preprocessor-time `IO_URING_CHECK_VERSION(IO_URING_VERSION_MAJOR, IO_URING_VERSION_MINOR)` guard and fails if the macro considers the current version insufficient.

State/persistence behavior: no runtime state beyond version values; no filesystem effects.

Dependencies/integration: depends only on liburing headers/library exposing consistent version information and helper exit constants.

Risks/test signals: failures indicate an inconsistency between compiled headers and linked library version reporting or a broken version comparison macro.
