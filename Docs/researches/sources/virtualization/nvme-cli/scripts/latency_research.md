# File Research: sources/virtualization/nvme-cli/scripts/latency

Shell script for simple QD=1 read/write latency sampling through nvme-cli.

Key elements:
- Accepts `-d DEVICE`, `-n COUNT`, and `-w` for write mode.
- Requires a nonzero count and a device path.
- Runs `make clean` and `make install` before tests.
- In read mode, repeatedly runs `nvme read` with `--latency`.
- In write mode, creates random data, runs `nvme write` with `--latency`, and warns that write mode can overwrite drive data.
- Extracts latency values into `latency.dat` and computes average microseconds with `bc`.

Notes:
- This is a destructive-capable manual helper, not a Meson test.
- Assumes the `nvme` command installed by `make install` is used.
