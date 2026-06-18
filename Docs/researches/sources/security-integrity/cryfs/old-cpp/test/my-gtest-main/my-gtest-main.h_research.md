# sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.h

Purpose: exposes the shared test executable path accessor.

Important APIs/types: declares `const boost::filesystem::path& get_executable();`.

Control flow/state: callers receive a reference to process-global state set by `main()`.

Dependencies/integration: includes Boost filesystem path and is public through the `my-gtest-main` target.

Risks: invalid to call before the common `main()` initializes the optional path, though normal linked test executables satisfy that.

Test signals: compile-time coverage from tests including this header.
