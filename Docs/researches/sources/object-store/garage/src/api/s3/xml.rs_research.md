# sources/object-store/garage/src/api/s3/xml.rs

Purpose: defines the S3 API XML serialization DTOs used by Garage's S3 front end. The file re-exports common XML helpers (`to_xml_with_header`, namespace serializers, `Value`, `IntValue`) and provides strongly named response structs matching AWS S3 XML element names via serde rename attributes.

Important APIs/types/functions: `Bucket`, `Owner`, `BucketList`, `ListAllMyBucketsResult`, `LocationConstraint`, delete-result structures, multipart upload/list/list-parts structures, list-objects structures, `VersioningConfiguration`, `PostObject`, and ACL structures (`Grantee`, `Grant`, `AccessControlList`, `AccessControlPolicy`). The types are plain `Serialize` structs, mostly using `Value` for escaped string content and `IntValue` for numeric XML text. Optional fields use `skip_serializing_if` where AWS omits absent elements.

Control flow: there is no runtime logic beyond serde-driven serialization. Callers construct the relevant response struct, then pass it to the common XML serializer. Namespace fields are represented as unit fields with custom serializer functions.

State and persistence: stateless; no persistence. It encodes API response state provided by bucket/object/multipart handlers.

Dependencies and integration points: depends on `serde::Serialize` and `garage_api_common::xml`. It integrates with S3 handlers that need AWS-compatible XML payloads and with `garage_util::time` in tests for RFC3339 timestamps.

Risks: compatibility is sensitive to element names, optionality, namespace placement, checksum field spelling, XML escaping, and empty-element behavior. Any change can break S3 clients even without compile errors. The file has no schema validation, so tests are the main guard against drift.

Test signals: extensive unit tests snapshot XML strings for errors, bucket listing, location/versioning/ACL, delete result, multipart initiation/completion/listing, list objects v1/v2, and list parts. These tests are strong regression signals for serialization shape and escaping.
