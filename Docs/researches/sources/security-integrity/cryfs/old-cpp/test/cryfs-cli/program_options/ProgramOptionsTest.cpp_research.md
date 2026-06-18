# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ProgramOptionsTest.cpp

Purpose: Tests the `ProgramOptions` value object directly. It verifies constructor/storage accessors for base/mount dirs, optional config/log/cipher/blocksize/idle settings, foreground and create flags, filesystem upgrade, integrity violation flags, and FUSE options.

Important APIs and types: Uses `ProgramOptions`, `ProgramOptionsTestBase`, Boost optional/gtest workaround, and GoogleTest.

Control flow: Tests construct `ProgramOptions` through fixture helpers with selected fields set or unset, then assert each getter returns the expected value.

State and persistence behavior: Pure in-memory immutable or value-like option state. No filesystem access beyond path object values.

Dependencies and integration points: Parser tests and CLI setup tests depend on this object faithfully carrying parsed configuration.

Risks: Defaults are important: false vs true and `none` vs explicit value must stay stable. Getter changes can ripple into CLI behavior.

Test signals: Exact path values, optional none/some states, boolean flags, numeric settings, integrity option combinations, and empty/non-empty FUSE option vectors.
