# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/fsck/BlockIdDetails.java

Purpose: `BlockIdDetails` is a simple fsck data carrier describing which volume, bucket, and key own a block.

Important APIs and types: It has getters and setters for `bucketName`, `blockVol`, and `keyName`, plus `toString`, `equals`, and `hashCode`.

Control flow and state: It is mutable and stores only three string fields.

Dependencies and integration points: `ContainerMapper` creates instances while mapping container IDs and local block IDs back to OM key metadata.

Risks: Field name `blockVol` is less clear than volume name. Mutability means map values can be changed after insertion. There is no JSON annotation, so Jackson uses bean naming.

Test signals: Tests should verify equality, hash code, string format if relied upon, and JSON serialization shape through `ContainerMapper`.
