# sources/object-store/rustfs/crates/signer/src/utils.rs

## Purpose
Provides signer utility functions for host resolution, SigV4 whitespace normalization, and pair sorting.

## Important APIs and Functions
`HostAddrError` distinguishes invalid UTF-8 Host header and missing URI host. `try_get_host_addr` gets the URI host:port and prefers a differing valid Host header. `get_host_addr` is a legacy string-returning wrapper that falls back to Host header for relative URIs or URI host when Host is invalid. `sign_v4_trim_all` collapses runs of whitespace to one space. `stable_sort_by_first` sorts pairs by the first element.

## Control Flow and State
No persistence or state. Host resolution reads headers and URI components, preserving ports when present.

## Integration Points
SigV2 uses `try_get_host_addr` for presign credential selection. SigV4 uses it to canonicalize the required `host` header. Tests rely on `http::request` and `s3s::Body`.

## Risks
`try_get_host_addr` requires a URI host even if a valid Host header exists; this is stricter than the legacy `get_host_addr` and can reject relative requests. Host comparison is exact and does not normalize case or default ports. `stable_sort_by_first` uses Rust's slice sort, which is stable, but the function name's stability property is inherited from std behavior.

## Test Signals
Unit tests cover preferring an explicit differing Host header, preserving host:port, legacy relative-URI fallback, invalid Host header rejection, URI fallback on invalid Host for legacy API, and relative URI rejection for the fallible API.
