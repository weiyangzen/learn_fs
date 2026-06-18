# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/logging.h

## Purpose
Defines the thin logging facade and logger interface used by assertion, process, and utility code. This specific file has 92 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ERROR_TYPE`, `WARN_TYPE`, `INFO_TYPE`, `DEBUG_TYPE`, `LogType`. Macros/constants: `MESSMER_CPPUTILS_LOGGING_LOGGING_H`. Important declarations or call sites include `inline void setLogger(std::shared_ptr<spdlog::logger> newLogger) {`; `logger().setLogger(newLogger);`; `inline void reset() {`; `logger().reset();`; `inline void flush() {`; `logger()->flush();`; `inline void setLevel(ERROR_TYPE) {`; `logger().setLevel(spdlog::level::err);`; `inline void setLevel(WARN_TYPE) {`; `logger().setLevel(spdlog::level::warn);`. CMake commands used here include `logger`, `LOG`. Primary includes/dependencies visible in the file include `Logger.h`, `stdexcept`, `spdlog/fmt/ostr.h`, `spdlog/sinks/basic_file_sink.h`, `spdlog/sinks/msvc_sink.h`, `spdlog/sinks/syslog_sink.h`.

## Control Flow
Call sites use logging macros/facade functions; the concrete logger receives severity and formatted text while headers keep dependencies light.

## State and Persistence Behavior
Logging state is whatever concrete logger is configured by consumers; these headers primarily define call interfaces.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Logger.h`, `stdexcept`, `spdlog/fmt/ostr.h`, `spdlog/sinks/basic_file_sink.h`, `spdlog/sinks/msvc_sink.h`, `spdlog/sinks/syslog_sink.h`.

## Risks and Edge Cases
Logging macros should not introduce heavy formatting or side effects when disabled. Error logs may include sensitive paths or operational details.

## Test Signals
Compile-time tests plus assertion/backtrace integration are the strongest signals for this lightweight facade.
