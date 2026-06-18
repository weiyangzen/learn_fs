# sources/user-network-fs/rclone/backend/s3/provider/Petabox.yaml

## Purpose
Embedded S3 provider descriptor for Petabox Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Petabox`, `description` is `Petabox Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 5 entries (us-east-1, eu-central-1, ap-southeast-1, me-south-1, sa-east-1); endpoint: 6 entries (s3.petabox.io, s3.us-east-1.petabox.io, s3.eu-central-1.petabox.io, s3.ap-southeast-1.petabox.io, s3.me-south-1.petabox.io, plus 1 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Petabox` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Petabox` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
