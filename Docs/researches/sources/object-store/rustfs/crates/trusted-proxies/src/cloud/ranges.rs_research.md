# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/ranges.rs

Purpose: Provides standalone cloud/provider IP range utilities for Cloudflare, DigitalOcean, and Google Cloud.

Important APIs: `CloudflareIpRanges::fetch` returns a static Cloudflare IPv4/IPv6 list; `CloudflareIpRanges::fetch_from_api` fetches official v4/v6 text endpoints and falls back to static ranges; `DigitalOceanIpRanges::fetch` returns a static set of datacenter/load-balancer ranges; `GoogleCloudIpRanges::fetch` retrieves `cloud.json`.

Control flow: Each fetcher parses string CIDRs into `IpNetwork`, logs structured success/failure details, and returns `AppError::cloud` only for construction/parsing errors that prevent normal operation. Cloudflare API attempts both URL sources independently, appends successful parsed ranges, and falls back only if both yield no ranges. Google Cloud returns an empty vector on HTTP/request failures instead of falling back to static data in this file.

State and dependencies: Stateless async helpers using `reqwest::Client`, `ipnetwork`, `serde` for GCP JSON, `Duration`, and `tracing`.

Integration points: Re-exported through `cloud/mod.rs`; likely contributes optional trusted proxy allowlists when cloud/provider mode is enabled.

Risks and tests: Cloudflare and DigitalOcean static ranges can age. Google Cloud parsing captures only `ipv4_prefix`, so IPv6 API prefixes are dropped. Returning `Ok(Vec::new())` for GCP fetch failures can hide provider range failures from callers. No direct tests in the requested test files cover these helper range fetchers.
