# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/gcp.rs

Purpose: Implements the GCP `CloudMetadataFetcher` for trusted proxy range discovery. `GcpMetadataFetcher` owns a `reqwest::Client` with caller-provided timeout and a metadata endpoint defaulting to `http://metadata.google.internal`.

Important APIs: `new`, `provider_name`, `fetch_network_cidrs`, `fetch_public_ip_ranges`, private `get_metadata`, `subnet_mask_to_prefix_length`, `fetch_gcp_ip_ranges`, `default_gcp_ip_ranges`, and `default_gcp_network_ranges`. The trait methods expose provider name, internal network CIDRs, and public provider ranges.

Control flow: network CIDR discovery lists `instance/network-interfaces/`, parses numeric interface indices, fetches each interface IP and subnet mask concurrently with `tokio::try_join!`, converts masks to prefixes, and falls back to RFC1918/GCP-reserved defaults when metadata is unavailable or empty. Public IP discovery fetches `https://www.gstatic.com/ipranges/cloud.json`, deserializes `prefixes`, and currently keeps only `ipv4_prefix` values from the API; the static fallback includes both IPv4 and IPv6 literals.

State and dependencies: No persistence beyond the HTTP client. Depends on `async_trait`, `reqwest`, `serde`, `ipnetwork`, `tokio`, and structured `tracing`, and returns crate `AppError`.

Integration points: Re-exported through `metadata/mod.rs` and `cloud/mod.rs`; used wherever `CloudMetadataFetcher` implementations are selected. Test signals are indirect from cloud integration tests, which cover provider naming for AWS but do not exercise GCP metadata parsing.

Risks: `Client::builder().build()` falls back silently to `Client::new`; metadata endpoint is fixed and not injectable for tests. `subnet_mask_to_prefix_length` does not reject non-contiguous masks across octet boundaries such as `255.0.255.0` because it resets state per octet. API parsing ignores `ipv6Prefix`/camelCase if the JSON uses that spelling, while the fallback list includes IPv6.
