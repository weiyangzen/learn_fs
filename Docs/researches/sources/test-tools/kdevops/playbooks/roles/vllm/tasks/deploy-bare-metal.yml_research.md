# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-bare-metal.yml

Purpose: deploys vLLM as a systemd-managed bare-metal service, either containerized or directly installed in a Python virtual environment.

Important APIs/types/functions: Ansible block, `file`, `command`/`uri`, GPU detection via `nvidia-smi`, `set_fact`, Docker service/user/group tasks, `nvidia-container-toolkit`, `nvidia-ctk`, image pull with mirror fallback, service templates, Python venv/pip/git source install, systemd reload/restart/start, health check, and model listing.

Control flow: creates directories, detects GPU availability, branches to container runtime or direct install, configures Docker/GPU runtime if needed, selects and pulls image, writes container service unit or direct service unit, optionally writes config file, reloads systemd, restarts if unit/config changed, starts/enables service, waits for `/health`, queries `/v1/models`, and displays endpoint info.

State/persistence behavior: creates `/opt`/data directories, installs packages or Python env, pulls images, writes systemd unit/config files, and runs persistent service.

Dependencies/integration: depends on templates, vLLM image/source variables, Docker or Python/pip/git, NVIDIA tooling when GPU is present, and `vllm_bare_metal_*` variables.

Risks/test signals: GPU runtime setup and image mirror fallback are fragile; direct pip/source install may drift. Test signals are systemd active state, health endpoint response, model API response, and successful image/venv installation.
