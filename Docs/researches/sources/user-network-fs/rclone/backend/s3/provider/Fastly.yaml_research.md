# sources/user-network-fs/rclone/backend/s3/provider/Fastly.yaml

## Purpose
Embedded S3 provider descriptor for Fastly Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Fastly`, `description` is `Fastly Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 11 entries (au-east-1, eu-central, eu-south-1, eu-west-1, jp-central-1, plus 6 more); endpoint: 11 entries (au-east-1.object.fastlystorage.app, eu-central.object.fastlystorage.app, eu-south-1.object.fastlystorage.app, eu-west-1.object.fastlystorage.app, jp-central-1.object.fastlystorage.app, plus 6 more). Advanced booleans: none. Quirks: force_path_style=true, use_already_exists=false, use_multipart_etag=false, use_multipart_uploads=false, etag_is_not_md5=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Fastly` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Fastly` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
