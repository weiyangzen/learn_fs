<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/UnknownEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/UnknownEntityHandler.java

## Purpose

`UnknownEntityHandler` returns consistent path-not-found responses for namespace paths that cannot be resolved.

## Important APIs and Types

It implements all `EntityHandler` response methods by returning `ResponseStatus.PATH_NOT_FOUND` and, for summary, `EntityType.UNKNOWN`.

## Control Flow

There is no lookup logic. Each API method constructs the corresponding response DTO and sets the not-found status.

## State and Persistence

No state is written or read beyond base construction.

## Dependencies and Integration Points

It is created by `EntityHandler.getEntityHandler` when volume, bucket, directory, or key lookup fails.

## Risks and Edge Cases

The constructor passes null path and bucket handler to the base class; current methods do not use normalized path, but future additions must avoid dereferencing it. Endpoints usually wrap these responses in HTTP 200.

## Test Signals

Tests should cover unknown summary, DU, quota, and distribution bodies and verify endpoint HTTP semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/UnknownEntityHandler.java -->
