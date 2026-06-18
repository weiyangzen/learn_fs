## sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/azure.rs

Purpose: implements Azure metadata and public Service Tags fetching for trusted proxy CIDR discovery.

Important APIs/types/functions: `AzureMetadataFetcher` stores a timeout `reqwest::Client` and IMDS endpoint. `get_metadata(path)` calls Azure IMDS with `Metadata: true`. `fetch_azure_ip_ranges` downloads a hard-coded Microsoft Service Tags JSON URL, deserializes `values[].properties.address_prefixes`, and includes tags whose name contains `Azure` but not `ActiveDirectory`. `default_azure_ranges` and `default_azure_network_ranges` provide public and VNet fallback CIDRs. The `CloudMetadataFetcher` impl returns provider `azure`, fetches network CIDRs from IMDS `instance/network/interface`, and public ranges from `fetch_azure_ip_ranges`.

Control flow and state: IMDS network metadata is parsed into interface/subnet structs and converted from address plus prefix into CIDR strings. Empty or failed metadata falls back to private/reserved Azure network ranges. Public range request failure falls back to a large hardcoded IPv4/IPv6 range list; HTTP non-success returns empty public ranges.

Dependencies and integration points: called by `CloudDetector`; depends on reqwest, serde, `ipnetwork`, tracing, and `AppError`.

Risks: the Service Tags URL includes a date-specific filename (`ServiceTags_Public_20260126.json`), which will age and may disappear or become stale. Filtering tags by substring `Azure` is broad and may include more ranges than desired. Fallback public ranges are static and require maintenance. Metadata JSON shape assumptions must match Azure IMDS response exactly.

Test signals: no local tests in this file. Reliable coverage would require mocked IMDS/service-tag responses and fallback-path tests.
