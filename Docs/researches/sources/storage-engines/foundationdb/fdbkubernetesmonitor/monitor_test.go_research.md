# sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor_test.go

Purpose: focused unit tests for selected monitor behaviors: node metadata environment injection, restart backoff calculation, and configuration parsing.

Important APIs and functions: tests call `updateCustomEnvironmentFromNodeMetadata`, `getBackoffDuration`, and `readConfiguration`. They construct `monitor` instances directly with fake Kubernetes clients and temporary files.

Control flow: node-label tests first run with no node metadata, then with fake Node labels containing slash/dot characters. Backoff tests use a table of error counts. Config tests write JSON config files, set a temporary executable `fdbserverPath`, and optionally add the isolate annotation to the fake pod.

State and persistence behavior: temp files model the config and executable. Fake Kubernetes client state provides pod/node metadata. The custom environment map is mutated in place with `NODE_LABEL_...` keys.

Dependencies and integration points: depends on `api.ProcessConfiguration`, fake controller-runtime client, Kubernetes core types, Ginkgo/Gomega, and `k8s.io/apimachinery/pkg/util/json`.

Risks: tests cover only `readConfiguration`, not `loadConfiguration` annotation writes or process spawning. Invalid JSON, missing executable, incompatible-version binary path selection, and argument-generation failures are not fully explored here.

Test signals: confirms node label sanitization, quadratic backoff capped at 60 seconds, nil config on missing version, protocol-compatible binary path override, and isolate annotation forcing `RunServers=false`.
