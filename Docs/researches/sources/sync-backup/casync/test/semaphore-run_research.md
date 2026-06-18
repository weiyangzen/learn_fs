# sources/sync-backup/casync/test/semaphore-run

Purpose: CI helper script for Semaphore-style builds.

Important APIs/types/functions: installs Meson/Ninja when needed, configures builds, runs tests, and includes a 32-bit build/test lane with GCC flags.

Control flow/state: mutates build directories, package/user Python environment, and test artifacts. It exits on failures to signal CI status.

Dependencies/integration: complements Meson and shell test scripts for hosted CI coverage.

Risks/test signals: depends on specific distro package names, Python/pip behavior, compiler availability, and i386 toolchain support. It is valuable for environment coverage but brittle outside CI.

Source research group: `subset-b-009122`.
