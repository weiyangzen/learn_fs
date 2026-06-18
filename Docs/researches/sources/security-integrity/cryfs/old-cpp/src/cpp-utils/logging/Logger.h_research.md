# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/Logger.h

## Purpose
Defines the thin logging facade and logger interface used by assertion, process, and utility code. This specific file has 59 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Logger`. Macros/constants: `MESSMER_CPPUTILS_LOGGING_LOGGER_H`. Important declarations or call sites include `void setLogger(std::shared_ptr<spdlog::logger> logger) {`; `_logger->set_level(_level);`; `void reset() {`; `setLogger(_defaultLogger());`; `void setLevel(spdlog::level::level_enum level) {`; `_logger->set_level(_level);`; `return _logger.get();`; `static std::shared_ptr<spdlog::logger> _defaultLogger() {`; `static auto singleton = spdlog::stderr_logger_mt("Log");`; `Logger() : _logger(), _level() {`. CMake commands used here include `setLogger`, `Logger`, `reset`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `spdlog/spdlog.h`, `../macros.h`, `spdlog/sinks/stdout_sinks.h`.

## Control Flow
Call sites use logging macros/facade functions; the concrete logger receives severity and formatted text while headers keep dependencies light.

## State and Persistence Behavior
Logging state is whatever concrete logger is configured by consumers; these headers primarily define call interfaces.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `spdlog/spdlog.h`, `../macros.h`, `spdlog/sinks/stdout_sinks.h`.

## Risks and Edge Cases
Logging macros should not introduce heavy formatting or side effects when disabled. Error logs may include sensitive paths or operational details.

## Test Signals
Compile-time tests plus assertion/backtrace integration are the strongest signals for this lightweight facade.
