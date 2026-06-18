# sources/test-tools/kdevops/.github/actions/configure/action.yml

Purpose: composite GitHub Action that prepares a kdevops workspace for a CI workflow by selecting a defconfig, writing CI metadata, merging CI-safe config fragments, and running the top-level make.

Important APIs/types/functions: inputs include `ci_workflow`, `kernel_tree`, `kernel_ref`, `test_mode`, and `guest_os`. Important steps configure git identity/safe-directory, validate `defconfigs/<ci_workflow>`, write GitHub output via `scripts/github_output.sh`, create `ci.trigger`, `ci.subject`, `ci.ref`, `ci.result`, and `ci.commit_extra`, run `make defconfig-...` with `KDEVOPS_HOSTS_PREFIX`, `LINUX_TREE`, and `LINUX_TREE_REF`, merge config fragments with `scripts/kconfig/merge_config.sh`, and run `make -j$(nproc)`.

Control flow: fail early if the requested defconfig is missing; initialize pessimistic CI metadata; compute a unique host prefix from GitHub run identifiers and test mode; optionally set `KMOD_TIMEOUT` on specific hosts/workflows; run the selected defconfig; merge base DIY/CI config plus optional VM sizing and guest OS config; run the build/generation make target.

State/persistence behavior: writes `.config`, generated ansible variables/inventory files through make, CI metadata files, and GitHub step output. It also relies on `/mirror/<kernel_tree>.git` for kernel source references.

Dependencies/integration: integrates with defconfigs, kconfig merge tooling, GitHub context variables, local mirror layout, scripts for GitHub outputs, and the top-level Makefile dependency graph.

Risks/test signals: inputs are inserted into shell variables and make arguments; the workflow constrains many values but `kernel_ref` is free-form. Missing guest OS config fails intentionally. Test signals are generated `.config`, `.extra_vars_auto.yaml`, `extra_vars.yaml`, `ansible.cfg`, `hosts`, and a successful parallel `make`.
