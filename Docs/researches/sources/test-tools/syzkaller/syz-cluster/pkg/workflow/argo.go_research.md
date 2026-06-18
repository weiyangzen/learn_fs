## sources/test-tools/syzkaller/syz-cluster/pkg/workflow/argo.go

`ArgoService` implements the workflow `Service` interface using in-cluster Argo Workflows. It embeds YAML files from the package, loads `template.yaml`, creates an Argo workflow client for the `default` namespace, starts workflows labeled by session ID, and polls status/log output.

`Start` deep-copies the embedded template, sets `workflow-id=<sessionID>`, substitutes the `session-id` argument, and creates the workflow. `Status` lists workflows by label, maps Argo phases to `StatusRunning`, `StatusFinished`, or `StatusFailed`, and returns synthesized node logs. `generateLog` sorts node status by start time/name and records phase, timestamps, inputs, and outputs. `PollPeriod` recommends 30 seconds.

State is stored in Kubernetes/Argo workflow objects, not locally. Dependencies are Argo client-go types, Kubernetes in-cluster config, embedded filesystem, and YAML unmarshalling. Integration points are controller/session processing services that start and monitor workflows. Risks include hard-coded namespace, selecting the first workflow when multiple share a label, no context propagation to Kubernetes calls, and TODO image naming. Test coverage appears indirect through mock service support rather than this concrete Argo client.
