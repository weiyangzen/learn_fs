## sources/test-tools/syzkaller/syz-cluster/workflow/boot/workflow-template.yaml

This Argo `WorkflowTemplate` wraps `boot-action`. It accepts base/patched build IDs, test name, report-findings flag, and a required `kernel` artifact mounted at `/base`. It writes a JSON result to `/output/result.json` and exposes it as an output parameter.

The container requests KVM by mounting host `/dev/kvm` and running privileged, with sizable CPU/memory resources and emptyDir work/output volumes. Integration is with the main workflow template's base and patched boot steps. Risks include privileged host-device access, fixed artifact path `/base`, high resource requirements, and dependence on workflow parameter `session-id`.
