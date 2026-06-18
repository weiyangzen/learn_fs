## sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs_test.go

Purpose: Field-level tests for object attribute conversion helpers.

Important APIs/types/functions: OgleTest suite `objectAttrsTest` covers ACL conversions, `ObjectAttrsToBucketObject`, `SetAttrsInWriter`, `ConvertObjToMinObject`, `ConvertObjToExtendedObjectAttributes`, `ConvertMinObjectAndExtendedObjectAttributesToObject`, and `ConvertMinObjectToObject`.

Control flow: tests build representative SDK/internal objects with timestamps, metadata, MD5/CRC, ACLs, and extended fields, invoke conversion helpers, and assert each relevant output field. Nil input cases verify safe nil returns.

State and persistence behavior: all in-memory; no external services.

Dependencies and integration points: depends on Cloud Storage SDK objects, internal `gcs` types, OgleTest, and JSON API ACL types.

Risks: field-by-field expectations can lag when object schemas evolve. Some assertions compare map/slice identity values and time string forms rather than deep normalized semantics.

Test signals: strong adapter coverage; gaps include parse-error behavior for invalid custom time and deep-copy/aliasing guarantees for maps.
