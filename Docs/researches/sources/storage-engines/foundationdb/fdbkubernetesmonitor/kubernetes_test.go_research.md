# sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes_test.go

Purpose: validates `kubernetesClient` behavior with fake controller-runtime clients and informers. It documents pod/node watch setup, metadata retrieval, event-to-timestamp translation, and pod annotation updates.

Important APIs and functions: the tests call `createPodClient`, `getPodMetadata`, `getNodeMetadata`, `OnUpdate` indirectly through fake informers, and `updateAnnotations`. Test fixtures use `fake.NewClientBuilder`, `informertest.FakeInformers`, and `controllertest.FakeInformer`.

Control flow: setup creates a pod and node in a fake client and sets `FDB_POD_NAMESPACE`, `FDB_POD_NAME`, and `FDB_NODE_NAME`. The cache factory passed to `createPodClient` asserts those values. Event tests push pod updates through the fake informer and inspect `TimestampFeed`.

State and persistence behavior: fake Kubernetes API state records annotations written by server-side apply. Tests check the serialized current configuration annotation and JSON environment annotation, including recursive argument environment discovery and `BINARY_DIR`.

Dependencies and integration points: depends on Kubernetes API machinery, controller-runtime fake clients/cache, Ginkgo/Gomega, and API annotation constants. It is the primary test signal for `kubernetes.go`.

Risks: fake clients do not fully model API-server apply conflicts, RBAC failures, deletion timestamps, or informer cache timing. The tests cover happy-path annotation updates but not retry semantics.

Test signals: strong for watcher count when node watching is enabled/disabled, valid timestamp delivery, invalid timestamp suppression, isolate annotation reload triggers, and environment annotation shape.
