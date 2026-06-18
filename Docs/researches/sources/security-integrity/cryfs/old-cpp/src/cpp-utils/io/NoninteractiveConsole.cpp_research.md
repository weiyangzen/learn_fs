# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 29 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `NoninteractiveConsole::NoninteractiveConsole(shared_ptr<Console> baseConsole): _baseConsole(std::move(baseConsole)) {`; `bool NoninteractiveConsole::askYesNo(const string &/*question*/, bool defaultValue) {`; `void NoninteractiveConsole::print(const std::string &output) {`; `_baseConsole->print(output);`; `unsigned int NoninteractiveConsole::ask(const string &/*question*/, const vector<string> &/*options*/) {`; `throw std::logic_error("Tried to ask a multiple choice question in noninteractive mode");`; `string NoninteractiveConsole::askPassword(const string &question) {`; `return _baseConsole->askPassword(question);`. Primary includes/dependencies visible in the file include `NoninteractiveConsole.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `NoninteractiveConsole.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.
