# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.h

Purpose: `CryTestBase` is the reusable fixture for CryFS filesystem tests. It creates a temporary basedir, temporary config file, fake home directory, mock console, key provider, config file, and root `CryDir` so tests can manipulate files, directories, and symlinks through CryFS objects.

Important APIs/types/functions: It uses `CryDevice`, `CryDir`, `CryNode`, `CryOpenFile`, `CryPresetPasswordBasedKeyProvider`, `SCrypt::TestSettings`, `TempFile`, and `TestWithFakeHomeDirectory`. Helper methods include `CreateFile`, `CreateDir`, `CreateSymlink`, `Exists`, `configFile`, and `failOnIntegrityViolation`.

Control flow: The constructor builds/load-or-creates a config, opens a CryFS device, obtains the root directory, and exposes helper wrappers that forward to the CryFS filesystem API. Tests inherit the fixture and directly create or inspect nodes under `_root`.

State and persistence behavior: Persistent test state lives in temp basedir/config paths and local-state home metadata. Runtime state includes the open device, root directory, derived key, and mock console expectations.

Dependencies and integration points: It binds configuration loading, key derivation, local state, and filesystem object APIs into one fixture used by rename, filesystem, and fs-interface integration tests.

Risks: Shared fixture setup means failures in config/key loading can cascade across many filesystem tests. Because it opens real CryFS objects, cleanup and temp directory isolation are important.

Test signals: Downstream tests observe node creation, existence checks, parent pointer updates, config file stability, and absence of integrity violations.
