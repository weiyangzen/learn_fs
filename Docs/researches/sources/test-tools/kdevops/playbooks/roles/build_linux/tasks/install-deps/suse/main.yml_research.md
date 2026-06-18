<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml

Source read: complete file, 24 lines, 695 bytes, sha256 `4fbc28b48f992a64`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family installation of build-linux timing and visualization packages.

Important APIs/types/functions: `community.general.zypper` installs `time`, `python3-matplotlib`, and `python3-numpy`, gated by `kdevops_workflow_enable_build_linux|default(false)|bool`.

Control flow: two package tasks run when the build-linux workflow flag is true.

State and persistence behavior: mutates zypper package state and leaves the tools installed for future benchmark runs.

Dependencies and integration: imported by the build-linux OS dispatcher and supports result statistics/plotting.

Risks: old SLE repos may not provide the Python visualization packages without repo preparation. No retry or repo refresh is performed.

Test signals: SUSE dry runs should skip unless enabled; real enabled runs should leave `time` and importable numpy/matplotlib available.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/suse/main.yml -->
