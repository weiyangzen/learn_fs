# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/HomedirTest.cpp

Purpose: Tests home-directory and application-data directory helpers, including fake home directory RAII overrides.

Important APIs and types: Uses `cpp-utils/system/homedir.h`, `TempDir`, and GoogleTest.

Control flow: Tests verify the real home directory exists, app-data path is valid, fake home directory scopes set and reset home/appdata values, and temp fake home uses distinct home/appdata directories.

State and persistence behavior: Reads real environment/system home paths and temporarily overrides process-level home directory behavior. Temporary directories are created and cleaned up.

Dependencies and integration points: CryFS CLI/config code depends on reliable home and app-data paths.

Risks: Platform differences in home/appdata conventions and environment variables can affect expectations. Fake overrides must restore global state.

Test signals: Existing home path, valid appdata path, correct fake path during scope, restored path after scope, and distinct temp fake dirs.
