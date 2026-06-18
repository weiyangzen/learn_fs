# sources/object-store/garage/src/rpc/consul.rs

Purpose: optional Consul service discovery integration for Garage RPC peers. It can query registered Garage nodes and publish the local node into either the Consul catalog API or local agent service API.

Important APIs and types: `ConsulDiscovery` holds `ConsulDiscoveryConfig` and a configured `reqwest::Client`. `new` builds TLS roots, optional client certificate identity for catalog API, optional invalid-cert acceptance, and token headers. `get_consul_nodes` returns `(NodeID, SocketAddr)` pairs. `publish_consul_service` registers the local node. `ConsulError` wraps IO, reqwest, invalid TLS config, and token-header errors. Internal structs model Consul's JSON shapes and use `META_PREFIX` for Garage metadata keys.

Control flow: reads query one or more configured datacenters, fetch `/v1/catalog/service/<service>`, deserializes entries, parses IP and Garage public key metadata, and skips malformed entries with warnings. Publishing constructs a deterministic service ID from the node key prefix, merges configured tags/meta, stores pubkey and hostname metadata, then PUTs to `catalog/register` or `agent/service/register?replace-existing-checks`.

State and persistence: no local persistent state. It reads certificate/key files at initialization and writes discovery state only into Consul.

Dependencies and integration: used by `System::discovery_loop` and `advertise_to_consul` behind `consul-discovery`. Relies on `garage_util::config`, `garage_net::NodeID`, `reqwest` rustls, and Consul HTTP API behavior.

Risks and test signals: malformed Consul metadata reduces discovery without failing the whole query. Catalog API requires cert/key pair consistency. Datacenter aggregation does not deduplicate nodes. No in-repo tests here; integration depends on external Consul availability and feature builds.
