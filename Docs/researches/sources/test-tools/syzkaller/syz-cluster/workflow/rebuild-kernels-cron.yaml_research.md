## sources/test-tools/syzkaller/syz-cluster/workflow/rebuild-kernels-cron.yaml

This Argo `CronWorkflow` periodically performs smoke builds of base kernels used by fuzz campaigns. It runs three times daily, replaces concurrent runs, queries `controller-service:8080/trees`, derives all unique kernel configs from fuzz targets, builds a request for every tree/config pair, and invokes the build workflow template with `smoke-build=true`.

State persists in Argo workflow executions and downstream build records/artifacts created by the build action. Integration points are controller `/trees`, build-action template, and tree/fuzz-target API schema. Risks include Python script JSON quoting through Argo parameters, `startingDeadlineSeconds: 0` skipping missed schedules, serial `parallelism: 1`, and hard-coded `amd64`.
