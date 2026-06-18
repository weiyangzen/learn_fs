# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ParserTest.cpp

Purpose: Tests command-line parsing for CryFS CLI options. It covers missing arguments, help, cipher listing, absolute/relative basedir and mountdir, foreground mode, filesystem upgrade, auto-create flags, logfile/config paths, cipher validation, idle unmount, blocksize, integrity options, and direct/indirect FUSE options.

Important APIs and types: Uses `Parser`, `ProgramOptions`, `ProgramOptionsTestBase`, `CryCiphers::supportedCipherNames`, `CryfsException`, `ErrorCode`, `CaptureStderrRAII`, Boost optional/filesystem, and gitversion support.

Control flow: `parse` builds an argv vector and calls `Parser(...).parse(...)`. Tests assert returned `ProgramOptions` fields or catch `CryfsException` and validate error code/output. FUSE option tests verify ordering before and after `--`.

State and persistence behavior: Parser state is in-memory. Relative paths depend on `boost::filesystem::current_path`. Captured stderr is process-local.

Dependencies and integration points: This is the contract between user CLI syntax and executable setup behavior.

Risks: Ordering of FUSE options, relative path normalization, and help/error output are compatibility-sensitive. Float idle values and boolean integrity parsing need precise conversion.

Test signals: Exact option fields, optional none/value states, invalid cipher error text, usage/cipher output, and FUSE option vector ordering.
