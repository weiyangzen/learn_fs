# sources/security-integrity/cryfs/old-cpp/test/gitversion/ParserTest.cpp

Purpose: provides comprehensive unit tests for `gitversion::Parser::parse`.

Important APIs/functions: each `TEST(ParserTest, ...)` parses a version string into `VersionInfo` and checks `majorVersion`, `minorVersion`, `hotfixVersion`, `isDevVersion`, `isStableVersion`, `gitCommitId`, `versionTag`, and `commitsSinceTag`.

Control flow: tests cover unknown versions, release strings with and without leading zeros, dirty release/dev builds, stable/alpha/rc/beta tags, missing minor/hotfix components, and git describe suffixes like `+20.g0123abcdef.dirty`.

State/persistence: no state beyond local `VersionInfo` values.

Dependencies/integration: includes gtest and `gitversion/parser.h`; validates the parser contract consumed by version display and comparison code.

Risks: expectations preserve string forms for numeric parts, including leading zeros, so changing parser normalization would break tests. The coverage is broad for accepted formats but not focused on invalid-input error handling.

Test signals: direct assertions make version parsing regressions easy to localize.
