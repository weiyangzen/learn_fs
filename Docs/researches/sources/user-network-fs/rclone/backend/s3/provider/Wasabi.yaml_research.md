# sources/user-network-fs/rclone/backend/s3/provider/Wasabi.yaml

## Purpose
Embedded S3 provider descriptor for Wasabi Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `Wasabi`, `description` is `Wasabi Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: empty/default-inheriting map; endpoint: 14 entries (s3.wasabisys.com, s3.us-east-2.wasabisys.com, s3.us-central-1.wasabisys.com, s3.us-west-1.wasabisys.com, s3.ca-central-1.wasabisys.com, plus 9 more); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `Wasabi` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `Wasabi` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
