## sources/test-tools/kdevops/workflows/minio/Kconfig

Purpose: Top-level MinIO workflow Kconfig for enabling MinIO Warp benchmarking.

Important APIs/types/functions: Main symbol is `KDEVOPS_WORKFLOW_ENABLE_MINIO_WARP`. When enabled, it sources `Kconfig.docker`, `Kconfig.storage`, and `Kconfig.warp`.

Control flow: The whole menu is gated by `KDEVOPS_WORKFLOW_ENABLE_MINIO`; Warp support defaults on and then pulls in docker/storage/warp subconfiguration.

State and persistence: Kconfig persists selections and YAML-output symbols from sourced files; this file itself writes no runtime state.

Dependencies and integration points: Integrates with MinIO Ansible roles, Docker/container settings, storage provisioning, and warp benchmark options.

Risks and test signals: Top-level enablement can hide sub-options if the parent workflow is disabled. Test by menuconfig/defconfig and checking generated extra-vars for MinIO subconfigs.
