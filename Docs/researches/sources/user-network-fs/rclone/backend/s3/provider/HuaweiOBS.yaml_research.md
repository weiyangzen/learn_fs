# sources/user-network-fs/rclone/backend/s3/provider/HuaweiOBS.yaml

## Purpose
Embedded S3 provider descriptor for Huawei Object Storage Service. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `HuaweiOBS`, `description` is `Huawei Object Storage Service`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 15 entries (af-south-1, ap-southeast-2, ap-southeast-3, cn-east-3, cn-east-2, plus 10 more); endpoint: 15 entries (obs.af-south-1.myhuaweicloud.com, obs.ap-southeast-2.myhuaweicloud.com, obs.ap-southeast-3.myhuaweicloud.com, obs.cn-east-3.myhuaweicloud.com, obs.cn-east-2.myhuaweicloud.com, plus 10 more); acl: empty/default-inheriting map. Advanced booleans: bucket_acl. Quirks: list_url_encode=false, list_version=1, use_already_exists=false.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `HuaweiOBS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `HuaweiOBS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
