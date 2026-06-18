# sources/user-network-fs/rclone/backend/s3/provider/ImpossibleCloud.yaml

## Purpose
Embedded S3 provider descriptor for Impossible Cloud Object Storage. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `ImpossibleCloud`, `description` is `Impossible Cloud Object Storage`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 7 entries (eu-central-2, eu-west-1, eu-west-2, eu-west-3, eu-east-1, plus 2 more); endpoint: 7 entries (eu-central-2.storage.impossibleapi.net, eu-west-1.storage.impossibleapi.net, eu-west-2.storage.impossibleapi.net, eu-west-3.storage.impossibleapi.net, eu-east-1.storage.impossibleapi.net, plus 2 more); location_constraint: empty/default-inheriting map; acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: none; S3 defaults apply.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `ImpossibleCloud` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `ImpossibleCloud` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
