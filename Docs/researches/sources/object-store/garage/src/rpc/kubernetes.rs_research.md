# sources/object-store/garage/src/rpc/kubernetes.rs

Purpose: optional Kubernetes peer discovery and advertisement through a `GarageNode` custom resource.

Important APIs and types: `Node` is the spec for the generated `GarageNode` CRD, with hostname, IP address, and RPC port. `create_kubernetes_crd` applies the CRD cluster-wide. `get_kubernetes_nodes` lists namespaced `GarageNode`s by service label and returns `(NodeID, SocketAddr)`. `publish_kubernetes_node` creates or replaces the object named by the hex node ID.

Control flow: CRD creation uses server-side apply with field manager `garage.deuxfleurs.fr`. Listing builds a label selector `garage.deuxfleurs.fr/service=<service>`, logs found object names, decodes each object name as a Garage public key, and returns only valid IDs. Publishing builds a `GarageNode`, inserts the same service label, then performs `get`; if the object exists, it preserves `resource_version` and calls `replace`, otherwise it calls `create`.

State and persistence: no local persistence. Cluster-visible state is the CRD and one custom resource per advertised node in the configured namespace.

Dependencies and integration: feature-gated through `kubernetes-discovery`, called by `System::discovery_loop` and `advertise_to_kubernetes`. Depends on `kube`, `k8s-openapi`, `schemars`, Serde, and `garage_util::config::KubernetesDiscoveryConfig`.

Risks and test signals: requires Kubernetes credentials and RBAC for CRDs and namespaced resources. Object name equals node public key hex, so invalid names are silently ignored on read. Replace can race with other writers if resource versions change. No direct tests; validation is mainly compile/feature and live-cluster integration.
