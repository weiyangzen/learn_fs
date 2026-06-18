# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/main_unmount.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 39 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `int main(int argc, const char *argv[]) {`; `if (!IsWindows7SP1OrGreater()) {`; `exit(1);`; `cpputils::showBacktraceOnCrash();`; `cryfs_unmount::Cli().main(argc, argv);`; `catch (const cryfs::CryfsException &e) {`; `if (e.what() != std::string()) {`; `return exitCode(e.errorCode());`; `catch (const std::runtime_error &e) {`; `return exitCode(ErrorCode::UnspecifiedError);`. CMake commands used here include `if`, `exit`, `catch`. Primary includes/dependencies visible in the file include `Windows.h`, `VersionHelpers.h`, `iostream`, `cryfs/impl/CryfsException.h`, `cpp-utils/assert/backtrace.h`, `Cli.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `Windows.h`, `VersionHelpers.h`, `iostream`, `cryfs/impl/CryfsException.h`, `cpp-utils/assert/backtrace.h`, `Cli.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.
