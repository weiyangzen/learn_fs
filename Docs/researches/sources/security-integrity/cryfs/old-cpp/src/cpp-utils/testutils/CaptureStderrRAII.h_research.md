# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/CaptureStderrRAII.h

## Purpose
Provides test-only RAII and expectation helpers for capturing stderr and checking exception behavior. This specific file has 46 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CaptureStderrRAII`. Macros/constants: `MESSMER_CPPUTILS_CAPTURESTDERRRAII_H`. Important declarations or call sites include `CaptureStderrRAII() {`; `_oldBuffer = std::cerr.rdbuf();`; `std::cerr.rdbuf(_buffer.rdbuf());`; `~CaptureStderrRAII() {`; `std::cerr.rdbuf(_oldBuffer);`; `std::string get_stderr() const {`; `return _buffer.str();`; `void EXPECT_MATCHES(const std::string &regex) {`; `EXPECT_TRUE(std::regex_search(get_stderr(), std::regex(regex, std::regex::basic)));`; `DISALLOW_COPY_AND_ASSIGN(CaptureStderrRAII);`. CMake commands used here include `CaptureStderrRAII`, `EXPECT_TRUE`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cpp-utils/macros.h`, `iostream`, `gmock/gmock.h`, `regex`.

## Control Flow
Test helpers wrap a scope around stderr redirection or exception assertions so tests can express expected failure behavior with minimal boilerplate.

## State and Persistence Behavior
State is scoped to a test and restored in destructors.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/macros.h`, `iostream`, `gmock/gmock.h`, `regex`.

## Risks and Edge Cases
Test helpers can mask unexpected exceptions if predicates are too broad, and stderr capture must restore descriptors even on failure.

## Test Signals
Validate helper self-tests by capturing known stderr output and matching expected exception types/messages.
