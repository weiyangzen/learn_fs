# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.h

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ProgramOptions`. Macros/constants: `MESSMER_CRYFSUNMOUNT_PROGRAMOPTIONS_PROGRAMOPTIONS_H`. Important declarations or call sites include `ProgramOptions(boost::filesystem::path mountDir, bool immediate);`; `const boost::filesystem::path &mountDir() const;`; `bool mountDirIsDriveLetter() const;`; `bool immediate() const;`; `DISALLOW_COPY_AND_ASSIGN(ProgramOptions);`. CMake commands used here include `ProgramOptions`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `vector`, `string`, `boost/optional.hpp`, `cpp-utils/macros.h`, `boost/filesystem.hpp`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `vector`, `string`, `boost/optional.hpp`, `cpp-utils/macros.h`, `boost/filesystem.hpp`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.
