# sources/user-network-fs/rclone/backend/s3/provider/FileLu.yaml

## Purpose
Embedded S3 provider descriptor for FileLu S5 (S3-Compatible Object Storage). It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `FileLu`, `description` is `FileLu S5 (S3-Compatible Object Storage)`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (global, us-east, eu-central, ap-southeast, me-central); endpoint: 5 entries (s5lu.com, us.s5lu.com, eu.s5lu.com, ap.s5lu.com, me.s5lu.com); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_version=2, force_path_style=true, list_url_encode=false, use_multipart_etag=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `FileLu` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `FileLu` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
