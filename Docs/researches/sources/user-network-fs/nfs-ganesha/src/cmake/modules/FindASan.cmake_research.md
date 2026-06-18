# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindASan.cmake

Purpose: Sanitizer module for AddressSanitizer support on targets that opt into sanitizer helpers.

Important APIs/types/functions: Defines option `SANITIZE_ADDRESS`, candidate compiler flags, incompatibility check with thread/memory sanitizers, includes `sanitize-helpers`, finds optional `asan-wrapper`, and defines `add_sanitize_address(TARGET)`.

Control flow: If ASan is enabled, compiler flags are probed through `sanitizer_check_compiler_flags`; target calls add the selected flags via `sanitizer_add_flags`.

State and persistence behavior: CMake option/cache state only.

Dependencies and integration points: Integrates with shared sanitizer helper macros and target-level `add_sanitizers` usage.

Risks: Mutually exclusive sanitizer checks only cover thread/memory, not all possible sanitizer conflicts. Wrapper discovery depends on `CMAKE_MODULE_PATH`.

Test signals: Configure ASan on/off, with TSan/MSan conflict, and compile a sanitized target.
