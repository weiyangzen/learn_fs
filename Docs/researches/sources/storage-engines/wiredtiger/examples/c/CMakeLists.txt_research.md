# sources/storage-engines/wiredtiger/examples/c/CMakeLists.txt

Purpose: declares the C example programs as build/test targets using the repository's `define_c_test` helper.

Important APIs and control flow: each example target maps one source file to a test directory and passes `-h $<SHELL_PATH:$<TARGET_FILE_DIR:target>/WT_HOME>` so the program uses a per-target home. POSIX-only examples (`ex_backup`, `ex_log`, `ex_smoke`) declare `DEPENDS "WT_POSIX"`. Non-MSVC builds link `ex_encrypt` and `ex_file_system` with `-rdynamic` so local extension entry points can be resolved at runtime.

State and persistence: generated tests create WT_HOME directories under their target binary folders and may create additional test directories during execution. The CMake file itself stores no runtime state.

Dependencies and integration: depends on the test helper macro, target generator expressions, WiredTiger libraries, and platform feature variable `WT_POSIX`. `-rdynamic` is an integration requirement for examples using `extensions=(local=...)`.

Risks: adding a new local-extension example without `-rdynamic` on ELF platforms can produce runtime extension lookup failures. POSIX gating must stay aligned with code using shell utilities, file descriptors, or POSIX threading.

Test signals: CMake configuration should enumerate all targets, and `ctest`/example execution validates per-target home isolation and platform gating.
