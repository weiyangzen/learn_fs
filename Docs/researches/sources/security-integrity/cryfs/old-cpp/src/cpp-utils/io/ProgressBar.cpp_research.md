# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: ProgressBar(std::make_shared<IOStreamConsole>(), preamble, max_value) {}`; `, _lastPercentage(std::numeric_limits<decltype(_lastPercentage)>::max()) {`; `ASSERT(_max_value > 0, "Progress bar can't handle max_value of 0");`; `_console->print("\n");`; `update(0);`; `void ProgressBar::update(uint64_t value) {`; `if (percentage != _lastPercentage) {`; `_console->print(_preamble + std::to_string(percentage) + "%");`. CMake commands used here include `ASSERT`, `update`, `if`. Primary includes/dependencies visible in the file include `ProgressBar.h`, `iostream`, `limits`, `mutex`, `IOStreamConsole.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ProgressBar.h`, `iostream`, `limits`, `mutex`, `IOStreamConsole.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.
