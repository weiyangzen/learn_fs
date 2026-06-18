<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/KeyEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/KeyEntityHandler.java

## Purpose

`KeyEntityHandler` implements namespace APIs for a single key/file path.

## Important APIs and Types

It returns `NamespaceSummaryResponse` with `KeyObjectDBInfo`, `DUResponse` for the key's size, type-not-applicable quota, and type-not-applicable file-size distribution.

## Control Flow

Summary maps the `OmKeyInfo` returned by the bucket handler into `KeyObjectDBInfo` and reports zero child keys with directory/bucket/volume counts set to not-applicable values. DU reads the key, returns data size, and optionally replicated size. Quota and distribution return `TYPE_NOT_APPLICABLE`.

## State and Persistence

It writes nothing and reads the key from the appropriate OM key/file table via `BucketHandler.getKeyInfo`.

## Dependencies and Integration Points

It is created by `EntityHandler` when a layout-specific `BucketHandler.determineKeyPath` returns `KEY`.

## Risks and Edge Cases

`getDuResponse` does not null-check `keyInfo`, relying on prior classification. Object metadata shape depends on `KeyObjectDBInfo` and layout-specific key names.

## Test Signals

Tests should cover FSO, legacy, and OBS key lookup, replica DU, missing key after classification race, and type-not-applicable responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/KeyEntityHandler.java -->
