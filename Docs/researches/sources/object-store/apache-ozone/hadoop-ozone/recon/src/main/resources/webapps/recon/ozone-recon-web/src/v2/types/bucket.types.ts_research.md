# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/bucket.types.ts

Purpose: Declares v2 bucket API, state, and table prop types.

Important APIs/types/functions: Exports `BucketStorageTypeList`/`BucketStorage`, `BucketLayoutTypeList`/`BucketLayout`, `Bucket`, `BucketResponse`, `BucketsState`, and `BucketsTableProps`. It imports `Acl` and v2 multi-select `Option`.

Control flow: Type module only. Constants are used by table filters and UI display; interfaces shape API transformation and component props.

State and persistence: No runtime state. `BucketsState` models page-local state including `volumeBucketMap`, selected bucket collections, and column/volume options.

Dependencies and integration points: Couples bucket UI to Ozone Manager storage type and bucket layout enums, ACL display, and table/select components.

Risks: Backend enum additions need list updates. `volumeBucketMap: Map<string, Set<Bucket>>` stores object identities, so duplicate bucket records are only deduplicated by object reference. `acls` is optional and consumers must handle absence.

Test signals: Compile and component tests should verify filter options align with supported backend enum values, ACL-optional buckets render safely, and table props support search by name and volumeName.
