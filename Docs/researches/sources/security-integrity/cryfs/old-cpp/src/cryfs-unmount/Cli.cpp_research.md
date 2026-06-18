# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 58 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void _showVersion() {`; `void Cli::main(int argc, const char **argv) {`; `_showVersion();`; `ProgramOptions options = Parser(argc, argv).parse();`; `if (!boost::filesystem::exists(options.mountDir())) {`; `throw cryfs::CryfsException("Given mountdir doesn't exist", cryfs::ErrorCode::InaccessibleMountDir);`; `bool immediate = options.immediate();`; `if (options.immediate()) {`; `if (options.immediate()) {`; `if (immediate) {`. CMake commands used here include `_showVersion`, `if`. Primary includes/dependencies visible in the file include `Cli.h`, `fspp/fuse/Fuse.h`, `cryfs-unmount/program_options/Parser.h`, `gitversion/gitversion.h`, `cryfs/impl/CryfsException.h`, `iostream`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `Cli.h`, `fspp/fuse/Fuse.h`, `cryfs-unmount/program_options/Parser.h`, `gitversion/gitversion.h`, `cryfs/impl/CryfsException.h`, `iostream`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.
