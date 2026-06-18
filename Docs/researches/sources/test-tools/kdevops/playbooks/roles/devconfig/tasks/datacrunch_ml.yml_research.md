<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml

Source read: complete file, 111 lines, 3095 bytes, sha256 `4a764476cadcc953`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml_research.md`.

Purpose: DataCrunch-specific machine-learning development bootstrap for Debian-family instances.

Important APIs/types/functions: `ansible.builtin.apt` dist-upgrade and package install, `get_url` for a pinned `uv-installer.sh` checksum, `command` for installer and venv creation, `ansible.builtin.pip` for PyTorch, shell `modprobe -r` NVIDIA modules, `community.general.modprobe`, `community.general.npm` installing `@anthropic-ai/claude-code`, `copy` to `/etc/motd`, and `lineinfile` auto-activating the venv.

Control flow: upgrade Debian packages; install development/ML dependencies; download/verify/run/remove uv installer; create `~/.venv`; install torch into it; unload and reload NVIDIA kernel module stack; install Claude Code globally via npm; write MOTD; append venv activation to `.bashrc`.

State and persistence behavior: heavily mutates system package state, user home, Python virtualenv, kernel module state, global npm packages, `/etc/motd`, and shell startup behavior.

Dependencies and integration: tailored to DataCrunch GPU instances, Debian package names, Python 3.12 venv, npm, NVIDIA kernel modules, uv release assets, and PyTorch package availability.

Risks: `apt upgrade: dist` is broad. uv checksum/version must stay aligned. PyTorch install has no CUDA index selection, so installed wheel may not match GPU needs. Unloading NVIDIA modules can disrupt active workloads. Auto-sourcing venv in `.bashrc` affects all interactive shells.

Test signals: on a fresh DataCrunch Debian instance, verify package upgrade success, checksum validation, `uv` installed, venv activation, `python -c 'import torch'`, `nvidia-smi` after module reload, npm global command availability, and idempotent rerun behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/datacrunch_ml.yml -->
