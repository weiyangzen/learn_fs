# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.hdds.scm.storage` as low-level IO streams for uploading and downloading chunks from the container service.

## Important APIs and Types
It declares only the package and package-level Javadoc. The package contains block/chunk input streams, block output streams, buffer pools, commit watchers, strategy adapters, and multipart stream composition.

## Control Flow
No runtime control flow exists in this file.

## State and Persistence Behavior
No state or persistence behavior exists in this file.

## Dependencies and Integration Points
The package is integrated by Ozone client IO factories and higher key streams that need container-level block and chunk access.

## Risks
The descriptor is documentation-only. Risk is limited to stale package documentation if the package grows beyond upload/download stream responsibilities.

## Test Signals
No direct tests are expected for package-info.
