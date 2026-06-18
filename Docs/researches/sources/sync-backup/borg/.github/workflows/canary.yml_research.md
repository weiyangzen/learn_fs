# sources/sync-backup/borg/.github/workflows/canary.yml Research

## Purpose

`canary.yml` runs scheduled and manually triggered tests with unlocked Python requirements to detect upstream dependency breakages before they affect locked CI. It covers representative Linux/macOS tox environments and a Windows PyInstaller/test path.

## Important APIs, Types, and Functions

The workflow triggers daily at `07:00 UTC` and via `workflow_dispatch`, with read-only contents permissions. `canary_tests` uses a matrix of Ubuntu and macOS Python/toxenv combinations, installs system packages, installs `requirements.d/development.txt` rather than the lock file, installs Borg with the extra matching the FUSE backend, and runs tox with an override to use unlocked development requirements. `windows_canary` uses `msys2/setup-msys2@v2`, Borg's `scripts/msys2-install-deps development`, a system-site-packages venv, PyInstaller requirements, editable install with extras, binary build, and pytest.

## Control Flow

Each matrix entry provisions OS and Python dependencies, installs Borg, and runs the environment-specific test command. Linux package selection branches by toxenv substring for `llfuse`, `pyfuse3`, or `mfusepy`. Windows uses MSYS2 shell defaults and environment variables to avoid path conversion.

## State and Persistence Behavior

The workflow creates virtual environments, build outputs, and test result files inside ephemeral GitHub runners. It does not upload artifacts or coverage. No repository state is changed.

## Dependencies and Integration Points

It integrates with `tox`, `pytest`, Python versions 3.11-3.14, FUSE package variants, Homebrew bundle installation, MSYS2 dependency scripts, PyInstaller specs, and Borg extras (`cockpit`, FUSE backends, `s3`, `sftp`, `rclone` on Windows).

## Risks and Edge Cases

Unlocked requirements intentionally introduce instability, so failures are signal but may be noisy. The tox override depends on tox accepting `--override "env_run_base.deps=[-rrequirements.d/development.txt]"`. macOS `brew bundle install || true` can mask dependency setup failures. The Linux test command contains a branch for Windows toxenv names in a non-Windows job, likely defensive dead code. Windows canary has `if: true`, making temporary disablement manual.

## Test Signals

The primary signal is daily workflow status. Useful follow-up signals include tracking failures against dependency release dates, verifying tox override behavior, and comparing canary failures to locked CI to distinguish upstream breakage from repository regressions.
