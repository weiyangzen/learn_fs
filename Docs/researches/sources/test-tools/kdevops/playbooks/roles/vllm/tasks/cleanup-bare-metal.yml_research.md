# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/cleanup-bare-metal.yml

Purpose: cleanup routine for vLLM bare-metal and related local runtime artifacts.

Important APIs/types/functions: `systemd`, `file`, shell Docker commands, minikube stop/delete commands, and cleanup flags `vllm_cleanup_remove_binaries`/`vllm_cleanup_remove_data`.

Control flow: stops/removes the vLLM service and unit file, reloads systemd, stops/removes vLLM containers and images, stops/deletes minikube, optionally removes kubectl/minikube/helm binaries, optionally removes data directories, then reports completion.

State/persistence behavior: deletes systemd unit, containers/images, Kubernetes local cluster state, binaries, and data directories depending on flags.

Dependencies/integration: used by vLLM cleanup/teardown paths; depends on Docker, minikube, systemd, and root privileges for system paths.

Risks/test signals: shell Docker filters can remove more than intended if names/images match broadly; data cleanup is destructive. Test signals are absent service/container/image/minikube resources and idempotent rerun success.
