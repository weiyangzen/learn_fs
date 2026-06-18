# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.h

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 38 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Parser`. Macros/constants: `MESSMER_CRYFSUNMOUNT_PROGRAMOPTIONS_PARSER_H`. Important declarations or call sites include `Parser(int argc, const char **argv);`; `ProgramOptions parse() const;`; `static std::vector<std::string> _argsToVector(int argc, const char **argv);`; `static std::vector<const char*> _to_const_char_vector(const std::vector<std::string> &options);`; `static void _addAllowedOptions(boost::program_options::options_description *desc);`; `static void _showHelp();`; `[[noreturn]] static void _showHelpAndExit(const std::string& message, cryfs::ErrorCode errorCode);`; `[[noreturn]] static void _showCiphersAndExit(const std::vector<std::string> &supportedCiphers);`; `[[noreturn]] static void _showVersionAndExit();`; `static boost::program_options::variables_map _parseOptionsOrShowHelp(const std::vector<std::string> &options);`. CMake commands used here include `Parser`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `ProgramOptions.h`, `boost/program_options.hpp`, `cryfs/impl/ErrorCodes.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `ProgramOptions.h`, `boost/program_options.hpp`, `cryfs/impl/ErrorCodes.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.
