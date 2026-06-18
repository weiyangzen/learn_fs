# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/BucketLayoutAwareOMKeyRequestFactory.java

## Purpose
`BucketLayoutAwareOMKeyRequestFactory` instantiates the correct `OMKeyRequest` subclass for key-like operations based on the target bucket layout, especially distinguishing object-store and file-system-optimized buckets.

## Important APIs and Types
- Static `OM_KEY_REQUEST_CLASSES` maps a generated string key to request classes.
- Static initializer registers create directory/file/key, allocate block, commit, delete, rename, multipart, set times, and object-tagging request variants.
- `createRequest` validates volume/bucket names, resolves real bucket layout, builds the lookup key, and reflectively constructs the request.
- `addRequestClass`, `getRequestInstanceFromMap`, and `getKey` support registration and lookup.

## Control Flow
The static block registers one or two classes for each supported protobuf `Type`. FSO-specific classes are registered under keys with the bucket layout suffix; object-store classes use only the type name. `createRequest` rejects blank volume or bucket names with `OMException`, calls `OzoneManagerUtils.getBucketLayout` through the metadata manager to resolve link buckets, and looks up the class by `getKey(requestType, bucketLayout)`. If found, it obtains a constructor `(OMRequest, BucketLayout)` and invokes it. Reflection errors are logged and wrapped as `INTERNAL_ERROR`; missing mappings become `NOT_SUPPORTED_OPERATION`.

## State and Persistence Behavior
The only state is the static class map. The factory does not persist anything, but it determines which request class will validate, update metadata cache, and later write DB changes through the OM response path.

## Dependencies and Integration Points
It integrates with `OzoneManagerRatisUtils.createClientRequest`, `OMMetadataManager`, `BucketLayout`, and all key request subclasses. It relies on every registered request class exposing the `(OMRequest, BucketLayout)` constructor.

## Risks and Edge Cases
Adding a new key command requires registering all supported bucket layouts. `RenameKeys` only registers object-store in the visible map, so FSO requests for that command are intentionally unsupported unless handled elsewhere. Reflection defers constructor errors to runtime. Link-bucket layout resolution means metadata manager availability and bucket validation are part of request creation.

## Test Signals
Tests should cover mapping keys for object-store and FSO layouts, blank name errors, unsupported layout/type errors, constructor mismatch error handling, link bucket layout resolution, and every registered command type.
