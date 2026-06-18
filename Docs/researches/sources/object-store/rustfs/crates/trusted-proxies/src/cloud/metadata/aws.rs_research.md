## sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/aws.rs

Purpose: implements AWS-specific metadata and public range fetching for trusted proxy CIDRs.

Important APIs/types/functions: `AwsMetadataFetcher` holds a `reqwest::Client` and IMDS endpoint. `new(timeout)` builds a timeout client and defaults endpoint to `http://169.254.169.254`. Private `get_metadata_token` obtains an IMDSv2 token but is currently marked dead code. The `CloudMetadataFetcher` impl returns provider name `aws`, default VPC private ranges from `fetch_network_cidrs`, and downloads/parses `https://ip-ranges.amazonaws.com/ip-ranges.json` in `fetch_public_ip_ranges`, filtering services `EC2` and `CLOUDFRONT`.

Control flow and state: network CIDRs are hardcoded fallback ranges `10/8`, `172.16/12`, and `192.168/16`. Public range fetch returns parsed networks on success, but returns an empty vector for HTTP or request errors instead of propagating.

Dependencies and integration points: called by `CloudDetector` when AWS is detected or in `try_all_providers`. Depends on `reqwest`, serde JSON structs, `ipnetwork::IpNetwork::from_str`, tracing, and `AppError`.

Risks: IMDS token retrieval is unused, so no actual AWS instance metadata is queried for VPC/subnet data. Treating all EC2 and CloudFront public ranges as trusted proxies may be too broad for strict deployments. HTTP errors degrade to empty public ranges while private ranges are still included by the detector default combiner.

Test signals: no local tests in this file. Behavior is indirectly covered if cloud detector/provider tests exercise AWS fetcher with mocked network or default ranges.
