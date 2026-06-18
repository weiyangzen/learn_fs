# sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes.go

Purpose: wraps Kubernetes API/cache access for the monitor pod. It reads pod/node metadata, watches pod/node events, emits configuration timestamps, and writes annotations describing current monitor configuration and environment.

Important APIs and types: `kubernetesClient` embeds `client.Client`, carries `TimestampFeed`, pod namespace/name, optional node name, and a logger. `setupCache` creates an in-cluster controller-runtime cache filtered to the current pod and node. `createPodClient` wires informers and starts the cache. Methods include `getPodMetadata`, `getNodeMetadata`, `updateAnnotations`, `updateFdbClusterTimestampAnnotation`, `updateAnnotationsOnPod`, and informer callbacks `OnAdd`, `OnUpdate`, `OnDelete`.

Control flow: environment variables `FDB_POD_NAMESPACE`, `FDB_POD_NAME`, and `FDB_NODE_NAME` select watched objects. Pod updates compare isolate annotation changes first; a change sends `time.Now().Unix()` to force reload. Otherwise, the outdated-config-map annotation is parsed and sent to `TimestampFeed`.

State and persistence behavior: persistent state is Kubernetes pod annotations applied server-side with field owner `fdb-kubernetes-monitor` and forced ownership. Annotation updates are retried except for deletion, not-found, or forbidden conditions.

Dependencies and integration points: integrates with `monitor.watchPodTimestamps`, `monitor.updateCustomEnvironmentFromNodeMetadata`, and the operator API annotation constants. It uses controller-runtime cache/client, client-go retry logic, and Kubernetes core Pod/Node metadata.

Risks: `updateAnnotationsOnPod` snapshots metadata once before retries, so conflict retries do not refetch fresh annotations. `context.Background()` is used for apply inside the retry closure, detaching from caller cancellation. Missing environment variables can lead to empty selectors.

Test signals: `kubernetes_test.go` covers fake-client setup, optional node watcher behavior, timestamp emission for valid/invalid annotations, isolate annotation changes, and annotation payload generation.
