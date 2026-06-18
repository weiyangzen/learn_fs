# sources/user-network-fs/rclone/backend/s3/provider/Ceph.yaml

## Purpose
Embedded S3 provider descriptor for Ceph Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Ceph`, `description` is `Ceph Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: empty/default-inheriting map; location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map; server_side_encryption: 2 entries (AES256, aws). Advanced booleans: bucket_acl, sse_customer_algorithm, sse_customer_key, sse_customer_key_base64, sse_customer_key_md5, sse_kms_key_id. Quirks: list_version=1, force_path_style=true, list_url_encode=false, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Ceph` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Ceph` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
