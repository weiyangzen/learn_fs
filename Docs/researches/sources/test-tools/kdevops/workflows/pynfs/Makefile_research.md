# sources/test-tools/kdevops/workflows/pynfs/Makefile

## Purpose
Provides the kdevops Make target layer for the pynfs workflow. It maps Kconfig values into Ansible extra variables, defines targets to install/run/reset pynfs on baseline or dev hosts, displays JSON results, and launches HTML visualization.

## Important APIs, Types, and Functions
Important variables are `PYNFS_GIT`, `PYNFS_GIT_TAG`, `PYNFS_ARGS`, `WORKFLOW_ARGS`, `LAST_KERNEL`, `FIND_PATH`, `PATTERN`, and `XARGS_ARGS`. Important targets are `pynfs`, `pynfs-baseline`, `pynfs-dev-baseline`, `pynfs-dev-reset`, `pynfs-show-results`, `pynfs-visualize`, and `pynfs-help-menu`. The file appends `pynfs-help-menu` to `HELP_TARGETS`.

## Control Flow
At parse time, the Makefile strips quotes from `CONFIG_PYNFS_GIT` and `CONFIG_PYNFS_GIT_TAG`, appends them as `pynfs_git=` and `pynfs_git_tag=`, optionally adds `pynfs_pnfs_block='True'`, and appends the result to global `WORKFLOW_ARGS`. `LAST_KERNEL` is read from `workflows/pynfs/results/last-kernel.txt` if present, otherwise the newest non-`last-run` results directory is selected. `FIND_PATH` uses `last-run` when `LAST_KERNEL` matches the last-kernel file, otherwise a kernel-specific results directory. The run targets call `ansible-playbook` with host limits and tags against `$(KDEVOPS_PLAYBOOKS_DIR)/pynfs.yml`; visualization calls `scripts/workflows/pynfs/visualize_results.py`.

## State and Persistence Behavior
Persistent workflow state is outside the Makefile: Ansible modifies baseline/dev hosts, result JSON is collected under `workflows/pynfs/results/`, `last-kernel.txt` selects the most recent run, and `pynfs-visualize` writes `workflows/pynfs/results/$(LAST_KERNEL)/html/index.html`. `pynfs-show-results` reads JSON result files and streams their contents. Make variables can be overridden by the caller, notably `LAST_KERNEL`, `PATTERN`, and `XARGS_ARGS`.

## Dependencies and Integration Points
Requires kdevops global Make variables such as `Q`, `KDEVOPS_PLAYBOOKS_DIR`, and generated `CONFIG_PYNFS_*` symbols. Runtime dependencies include `ansible-playbook`, `extra_vars.yaml`, `find`, `xargs`, `sed`, `grep`, `ls`, and `python3`. It integrates directly with the `pynfs.yml` playbook and with the checked-in baseline JSON files consumed by result comparison/visualization.

## Risks
`LAST_KERNEL` discovery can become empty if no result directories exist, which makes downstream paths ambiguous. `pynfs-visualize` checks only the kernel-specific directory and will not visualize `last-run` directly unless the `LAST_KERNEL` mapping resolves to a real directory. `pynfs-show-results` allows caller-provided `PATTERN` and `XARGS_ARGS`, which is flexible but can execute arbitrary shell fragments. The visualization success line contains a Unicode check mark, unlike most ASCII-only Make output. The baseline and dev targets duplicate the two-playbook sequence, so tag changes must be kept in sync.

## Test Signals
Use `make -n pynfs`, `make -n pynfs-baseline`, `make -n pynfs-dev-baseline`, and `make -n pynfs-visualize LAST_KERNEL=<fixture>` to verify playbook paths, limits, tags, and extra vars. Fixture tests for `pynfs-show-results` should cover `last-kernel.txt`, newest-directory fallback, custom `PATTERN`, and missing result directories.
