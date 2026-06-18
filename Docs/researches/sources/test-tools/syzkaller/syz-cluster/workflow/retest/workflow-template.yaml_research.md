## sources/test-tools/syzkaller/syz-cluster/workflow/retest/workflow-template.yaml

This Argo template runs `retest-action` with optional base kernel, required patched kernel, and a retest task artifact. It passes base/patched build IDs, session ID, test name, and `/workdir`, with a four-hour timeout.

The container uses privileged `/dev/kvm`, an emptyDir workdir, and sizable CPU/memory resources. Integration is with main workflow retest-campaign and triage-generated `api.RetestTask`. Risks include host KVM privilege, optional base artifact handling, and no output artifact/parameter beyond status reported through APIs.
