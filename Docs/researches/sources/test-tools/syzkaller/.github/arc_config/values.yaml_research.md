<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/arc_config/values.yaml -->
# sources/test-tools/syzkaller/.github/arc_config/values.yaml research

Purpose: Helm values for deploying GitHub Actions Runner Controller scale-set runners for the syzkaller repository.

Important APIs, types, and functions: key fields include `githubConfigUrl`, `githubConfigSecret`, `containerMode.type: kubernetes`, a Kubernetes-mode PVC template with `ReadWriteOnce`, `openebs-hostpath`, and 1 Gi storage, plus a runner pod template requesting 31 CPUs.

Control flow: ARC and its Helm chart consume this values file to create listener and runner pods. Jobs execute inside Kubernetes-mode runner pods rather than Docker-in-Docker.

State and persistence: persistent state is external to the file: Kubernetes secrets, PVCs, runner registrations, and ephemeral work volumes. The checked-in file leaves `github_token` empty, so live credentials must be supplied separately.

Dependencies and integration: depends on the ARC chart, a compatible Kubernetes cluster, a storage class named `openebs-hostpath`, GitHub runner registration permissions, and high-CPU nodes.

Risks: an empty secret is safe for source control but unusable without deployment-time secret injection. The 31-CPU request can starve scheduling on smaller clusters. Kubernetes container mode requires job containers and volume behavior compatible with the workflows.

Test signals: Helm template/lint output, kube-linter findings, successful listener startup, runner registration in GitHub, PVC provisioning, and a CI job landing on a scale-set runner.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/arc_config/values.yaml -->
