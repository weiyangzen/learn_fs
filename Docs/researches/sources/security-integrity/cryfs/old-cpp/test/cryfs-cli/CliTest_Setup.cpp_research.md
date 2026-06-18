# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_Setup.cpp

Purpose: Tests CLI setup behavior for ordinary startup, log/config options, automatic basedir/mountpoint creation, FUSE options, and commas in basedir paths.

Important APIs and types: Uses `testutils/CliTest.h` and CLI fixture helpers for running CryFS with temporary directories.

Control flow: Tests run the CLI with different option combinations, inspect success/failure, and verify created directories or accepted paths/options. Failure cases cover autocreate permissions or impossible targets.

State and persistence behavior: Creates and mutates temporary basedirs, mountpoints, config/log paths, and possibly FUSE mount state through the fixture.

Dependencies and integration points: Covers the end-to-end CLI setup path from parsed options to filesystem/mount preparation.

Risks: Mount/FUSE availability and filesystem permissions can be environment-sensitive. Path parsing with commas is a regression-prone FUSE option boundary.

Test signals: Expected run success/error, created directories/files, accepted config/logfile options, passed FUSE options, and comma-containing basedir support.
