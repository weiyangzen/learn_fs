# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyLocationInfoGroup.java

Purpose: validates versioned block-location grouping in `OmKeyLocationInfoGroup`.

Important APIs/types/functions: exercises constructor, `getBlocksLatestVersionOnly`, `getLocationList(version)`, `generateNextVersion`, `getLocationList`, and `getVersion`.

Control flow and state: helper creates a group at version 2 containing two locations with create version 1 and one location with create version 2. Tests ensure latest-only returns the version 2 location, previous version lookup returns two locations, and generating the next version with a new list yields version 3.

Dependencies and integration points: depends on `OmKeyLocationInfo.Builder`. This data structure is used by `OmKeyInfo` to track block locations across key versions and multipart updates.

Risks and test signals: catches off-by-one version progression and incorrect filtering by create version. Persistence risk is moderate because location group ordering and versioning affect key reads and recovery.
