# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_tests/action.yaml

Purpose: Composite action that runs the legacy C++ test binaries after a build.

Important APIs and types: Inputs are `gtest_args` and `extra_env_vars`. It invokes the gitversion, cpp-utils, parallelaccessstore, blockstore, blobstore, cryfs, fspp, and cryfs-cli test executables depending on OS and matrix name.

Control flow: The script enters `build`, exports caller-provided env vars, runs core test binaries with the gtest filter arguments, then skips some macOS-only broken tests. On non-macOS it skips fspp under the TSAN matrix and otherwise runs fspp and cryfs-cli tests.

State and persistence behavior: Test execution can create test artifacts under the build tree or temp directories but this action manages no explicit persistence. Environment variables such as sanitizer options affect process behavior.

Dependencies and integration points: Called by `main.yaml` for Linux/macOS jobs where `matrix.run_tests` is true. It assumes build output paths match the Ninja layout.

Risks: `export ${{ inputs.extra_env_vars }}` is fragile if the input is empty or contains shell metacharacters. The action references `matrix.name` directly inside a composite action script, tying it to a specific workflow context. macOS and TSAN exclusions encode known gaps rather than full coverage.

Test signals: Nonzero exit from any test binary fails the CI job. The gtest filter and sanitizer environment are matrix-specific signals for compatibility and race/memory checks.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_tests/action.yaml` completely for this pass (38 lines, 1312 bytes).
