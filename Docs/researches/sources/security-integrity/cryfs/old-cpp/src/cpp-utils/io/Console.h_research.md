# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 27 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Console`. Macros/constants: `MESSMER_CPPUTILS_IO_CONSOLE_H`. Important declarations or call sites include `virtual unsigned int ask(const std::string &question, const std::vector<std::string> &options) = 0;`; `virtual bool askYesNo(const std::string &question, bool defaultValue) = 0; // NoninteractiveConsole will just return the defaul...`; `virtual void print(const std::string &output) = 0;`; `virtual std::string askPassword(const std::string &question) = 0;`. Primary includes/dependencies visible in the file include `string`, `vector`, `iostream`, `boost/optional.hpp`, `../macros.h`, `../pointer/unique_ref.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `string`, `vector`, `iostream`, `boost/optional.hpp`, `../macros.h`, `../pointer/unique_ref.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.
