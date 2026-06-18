<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-k8s.sh -->
# sources/test-tools/syzkaller/tools/check-k8s.sh

## Purpose

Kubernetes manifest validation for syzkaller agent and cluster deployment targets.

## Important APIs, Types, and Functions

Defines `run_checks`; invokes Make/Kustomize, kubeconform, and kube-linter via pinned `go run` module versions with mock deployment environment variables.

## Control Flow

Exports mock secrets/image vars, renders each Make target, validates rendered YAML with kubeconform, lints with kube-linter through process substitution, skips non-Linux hosts, and accumulates failures.

## State and Persistence Behavior

Keeps a shell `FAILED` flag and mock environment; manifests flow through variables/pipes and are not persisted.

## Dependencies and Integration Points

Requires Linux, Go module/network/cache access, target Makefiles, `.kube-linter.yaml`, and K8s schema tooling.

## Risks and Edge Cases

Pinned `go run` tools still depend on module availability; template variable drift can fail rendering before schema validation.

## Test Signals

Run in Linux CI and inject bad YAML/schema/linter fixtures to verify failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-k8s.sh -->
