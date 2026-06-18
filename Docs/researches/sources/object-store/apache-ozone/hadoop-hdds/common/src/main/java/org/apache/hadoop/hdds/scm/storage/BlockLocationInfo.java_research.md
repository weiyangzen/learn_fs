# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockLocationInfo.java

## Purpose
Represents one block location for a key segment: block ID, pipeline, length, offset, security token, creation version, multipart part number, and under-construction marker.

## Important APIs and types
The builder sets `BlockID`, `Pipeline`, length, offset, token, part number, and create version. Accessors expose container/local IDs and block commit sequence ID through `BlockID`. Mutators allow updating length, token, pipeline, part number, create version, and under-construction status.

## Control flow and state
This is a mutable value object. `hasSameBlockAs` compares block identity plus length, offset, and create version while ignoring token and pipeline. `equals` includes token and pipeline but omits part number and under-construction, so equality does not fully reflect all mutable fields.

## Dependencies and integration points
It connects key/block metadata to SCM pipelines and `OzoneBlockTokenIdentifier` Hadoop tokens. Client read/write paths use it to route block operations and carry auth material.

## Risks and test signals
Tests should cover equality semantics, `hasSameBlockAs`, mutable length/token/pipeline updates, and behavior when part number or under-construction changes are intentionally ignored. Mutable fields make it risky as a hash-map key.
