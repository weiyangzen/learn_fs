# sources/user-network-fs/rclone/backend/s3/provider/us3.yaml

## Purpose
Embedded S3 provider descriptor for US3 Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `US3`, `description` is `US3 Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: endpoint: 23 entries (s3-cn-bj.ufileos.com, s3-cn-wlcb.ufileos.com, s3-cn-sh2.ufileos.com, s3-cn-gd.ufileos.com, s3-hk.ufileos.com, plus 18 more); acl: 2 entries (private, public-read); storage_class: 3 entries (STANDARD, ARCHIVE, STANDARD_IA). Advanced booleans: bucket_acl. Quirks: list_version=1, use_multipart_etag=false, use_already_exists=false, list_url_encode=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `US3` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `US3` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
