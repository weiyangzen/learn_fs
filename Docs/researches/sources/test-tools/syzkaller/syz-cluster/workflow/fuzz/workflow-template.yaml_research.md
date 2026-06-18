## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/workflow-template.yaml

This Argo `WorkflowTemplate` runs the fuzz action for up to four hours. It accepts base/patched build IDs, test name, base/patched kernel artifacts mounted at `/base` and `/patched`, and config JSON mounted at `/tmp/config.json`. It invokes `/bin/fuzz-action` with a three-hour fuzzing timeout and verbose logging.

The template requests 24-30 CPUs, about 90-96G memory, privileged `/dev/kvm` access, and a workdir emptyDir. Integration is with `pkg/workflow/template.yaml` fuzz-campaign steps and build outputs containing `symbol_hashes.json`. Risks include high resource needs, privileged KVM access, reliance on `--vv` being accepted by global syzkaller flags, and no declared output artifacts.
