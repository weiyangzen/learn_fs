# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 131 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `:_options(_argsToVector(argc, argv)) {`; `vector<string> Parser::_argsToVector(int argc, const char **argv) {`; `result.push_back(argv[i]);`; `ProgramOptions Parser::parse() const {`; `po::variables_map vm = _parseOptionsOrShowHelp(_options);`; `if (!vm.count("mount-dir")) {`; `_showHelpAndExit("Please specify a mount directory.", ErrorCode::InvalidArguments);`; `bf::path mountDir = vm["mount-dir"].as<string>();`; `bool immediate = vm.count("immediate");`; `return ProgramOptions(std::move(mountDir), immediate);`. CMake commands used here include `for`, `if`, `_showHelpAndExit`, `catch`, `_showHelp`, `_addAllowedOptions`, `_addPositionalOptionForBaseDir`, `_showVersionAndExit`. Primary includes/dependencies visible in the file include `Parser.h`, `iostream`, `boost/optional.hpp`, `cryfs/impl/config/CryConfigConsole.h`, `cryfs/impl/CryfsException.h`, `cryfs-cli/Environment.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `Parser.h`, `iostream`, `boost/optional.hpp`, `cryfs/impl/config/CryConfigConsole.h`, `cryfs/impl/CryfsException.h`, `cryfs-cli/Environment.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.
