## sources/test-tools/syzkaller/syz-cluster/workflow/kustomization.yaml

This kustomization aggregates workflow resources: rebuild-kernels cron workflow, triage/build/boot/fuzz/retest workflow templates. It is the package-level manifest for installing workflow definitions.

State is in Kubernetes/Argo after application. Integration depends on the referenced build workflow template that is outside this subset. Risks include missing RBAC unless `permissions.yaml` is applied elsewhere, and no local image transformation in this kustomization.
