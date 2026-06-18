# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/generate_sample_data.py

## Purpose
Creates synthetic reboot-limit result data for testing the analyzer and visualization pipeline.

## Important APIs
`generate_sample_data(results_dir, num_hosts=2, num_boots=50)` creates host directories, writes `reboot-count.txt`, and writes repeated `systemctl-analyze.txt` lines with randomized kernel, initrd, userspace, and total boot times.

## Control flow
The first host is named `demo-reboot-limit`; additional hosts use a development-style name. Random variation and periodic slow boots are applied to make graphs non-flat. The script has a direct `__main__` path for sample generation.

## State and dependencies
Persists files under the requested results directory. Uses Python standard library `os`, `random`, and `pathlib`.

## Integration points
Feeds `analyze_results.py` without needing real reboot-limit workflow runs.

## Risks and test signals
Randomness means output is not deterministic unless seeded externally. Host naming for `i > 0` appears fixed to `demo-reboot-limit-dev`, so more than two hosts would collide. Test by generating into a scratch directory and running the analyzer over it.
