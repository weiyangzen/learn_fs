# sources/user-network-fs/rclone/backend/s3/provider/AWS.yaml

## Purpose
Embedded S3 provider descriptor for Amazon Web Services (AWS) S3. It is data consumed by the S3 backend to render provider choices, option examples, advanced-option relevance, and compatibility quirks.

## Important APIs, Types, And Functions
The file conforms to the `Provider`/`Quirks` YAML schema in `providers.go`: `name` is `AWS`, `description` is `Amazon Web Services (AWS) S3`, map fields define examples, boolean fields enable provider-specific advanced options, and `quirks` changes runtime S3 behavior. Map signals: region: 26 entries (us-east-1, us-east-2, us-west-1, us-west-2, ca-central-1, plus 21 more); endpoint: empty/default-inheriting map; location_constraint: 25 entries (us-east-2, us-west-1, us-west-2, ca-central-1, eu-west-1, plus 20 more); acl: empty/default-inheriting map; storage_class: 8 entries (STANDARD, REDUCED_REDUNDANCY, STANDARD_IA, ONEZONE_IA, GLACIER, plus 3 more); server_side_encryption: 2 entries (AES256, aws). Advanced booleans: bucket_acl, directory_bucket, leave_parts_on_error, requester_pays, sse_customer_algorithm, sse_customer_key, sse_customer_key_base64, sse_customer_key_md5, sse_kms_key_id, sts_endpoint, use_accelerate_endpoint. Quirks: might_gzip=false, use_unsigned_payload=false, use_data_integrity_protections=true.

## Control Flow
`//go:embed provider/*.yaml` embeds this file; `loadProviders` unmarshals it; `constructProviders` adds `AWS` to the `provider` option and merges examples into matching S3 options. Empty maps intentionally inherit defaults from `Other` where `providers.go` supplies that behavior.

## State And Persistence
The descriptor is immutable build-time data. User configs may persist `AWS` and selected endpoint/region/ACL/storage/encryption values derived from it.

## Dependencies And Integration Points
Integrated by `providers.go`, `yaml.v3`, ordered maps, and the main S3 backend. It affects endpoint selection, addressing style, list API behavior, multipart/checksum assumptions, ACL/storage-class/server-side-encryption choices, and copy/upload limits.

## Risks And Test Signals
Risks include stale provider endpoints, schema drift, wrong quirk defaults, duplicate provider names, and examples that no longer match provider behavior. Test signals are YAML unmarshal validation, provider example rendering, quirk regression tests, and live/mocked S3 compatibility checks for this provider.
