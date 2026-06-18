# File Research: sources/virtualization/nvme-cli/scripts/regress

Manual regression shell script for basic nvme-cli commands.

Key elements:
- Accepts `-d DEVICE`, `-w` for write mode, and `-l` to include `nvme list`.
- Requires a device path.
- Runs `make clean` and `make install`.
- Executes identify, namespace list, log, feature, flush, read, and optionally write/diff commands.
- Uses colorized pass/fail output and exits on first failure.
- Write mode uses random data and warns that it can overwrite the drive.

Role:
- Legacy/manual smoke test below the Python/Meson TAP test infrastructure.
