## sources/object-store/rustfs/crates/trusted-proxies/src/cloud/detector.rs

Purpose: detects the current cloud provider and fetches trusted proxy CIDR ranges from provider-specific metadata/range fetchers.

Important APIs/types/functions: `CloudProvider` supports AWS, Azure, GCP, DigitalOcean, Cloudflare, and `Unknown(String)`, with `FromStr`, `detect_from_env`, and `name`. `CloudMetadataFetcher` defines provider name, network CIDR fetch, public IP range fetch, and a default `fetch_trusted_proxy_ranges` that degrades independently on each dataset. `CloudDetector` stores enabled flag, timeout, and optional forced provider; methods include `new`, `detect_provider`, `fetch_trusted_ranges`, and `try_all_providers`. `default_cloud_detector` disables detection.

Control flow and state: provider detection is disabled-first, then forced-provider, then environment markers. Fetching dispatches to AWS/Azure/GCP metadata fetchers, Cloudflare/DigitalOcean range fetchers, or returns empty for unknown/none. `try_all_providers` sequentially tries AWS, Azure, and GCP until a non-empty result.

Dependencies and integration points: integrates with `AwsMetadataFetcher`, `AzureMetadataFetcher`, `GcpMetadataFetcher`, `CloudflareIpRanges`, and `DigitalOceanIpRanges`. Uses `rustfs_utils::get_env_opt_str`, `ipnetwork`, tracing, and crate `AppError`.

Risks: environment detection uses `RUSTFS_`-prefixed markers rather than raw cloud provider env names, so deployment adapters must set those markers. The default trait method returns `Ok` with partial data when one fetch fails, which is robust but can silently broaden/narrow trust depending on fallback behavior. Forced unknown providers return empty without error.

Test signals: tests cover AWS env detection preference and no-marker returning `None`. Fetch behavior relies on provider-specific tests elsewhere or integration tests.
