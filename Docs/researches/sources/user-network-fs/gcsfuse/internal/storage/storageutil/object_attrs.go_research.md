## sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs.go

Purpose: Converts between Cloud Storage SDK object attributes and gcsfuse internal object models, and applies internal create-object attributes to `storage.Writer`.

Important APIs/types/functions: ACL converters, `ObjectAttrsToBucketObject`, `ObjectAttrsToMinObject`, `SetAttrsInWriter`, `ConvertObjToMinObject`, `ConvertObjToExtendedObjectAttributes`, `ConvertMinObjectAndExtendedObjectAttributesToObject`, and `ConvertMinObjectToObject`.

Control flow: conversion functions copy fields directly, translate ACL project-team structures, convert MD5 slices to fixed arrays, copy CRC32C values so returned pointers do not alias SDK structs, and split/merge minimal versus extended object attributes.

State and persistence behavior: no persistence, but returned objects often share maps/slices from inputs except checksum scalar copies. `SetAttrsInWriter` mutates a supplied `storage.Writer` and enables `SendCRC32C` when CRC is present.

Dependencies and integration points: central adapter between `cloud.google.com/go/storage`, JSON storage v1 ACL structures, and internal `gcs` types used by bucket implementations and file-system metadata paths.

Risks: some fields are intentionally omitted, so SDK attribute additions require review. `SetAttrsInWriter` ignores `time.Parse` errors for custom time. Metadata maps are not deep-copied. Nil handling differs: merge requires both min and extended attributes non-nil.

Test signals: `object_attrs_test.go` provides broad field-by-field coverage for ACL conversion, writer assignment, nil handling, split/merge conversions, and default extended-field values.
