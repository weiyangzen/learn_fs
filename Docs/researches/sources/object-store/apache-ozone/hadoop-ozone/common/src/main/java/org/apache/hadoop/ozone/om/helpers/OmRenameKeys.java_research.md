<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRenameKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRenameKeys.java

## Purpose

`OmRenameKeys` packages a batch key-rename request for one volume and bucket. It carries a map from old key names to new key names and a map from old key names to the already-computed destination `OmKeyInfo`.

## Important APIs, Types, And Functions

The constructor accepts `volume`, `bucket`, `fromAndToKey`, and `fromKeyAndToKeyInfo`. Getters expose those fields to OM request handlers.

## Control Flow, State, And Persistence

The class is a mutable-field DTO, but it has no mutator methods after construction. Rename logic consumes the maps while updating OM key tables through the normal write path. The object is not itself persisted.

## Dependencies And Integration Points

It depends on `Map`, `HashMap`, and `OmKeyInfo`. It integrates with `OzoneManagerProtocol.renameKeys`, file-system optimized rename handling, and audit/request conversion code that needs both names and destination metadata.

## Risks And Test Signals

The constructor stores caller-supplied map references directly, so later external mutation can alter request content. Tests should cover empty batches, missing destination `OmKeyInfo`, duplicate target names, atomicity of partial failures, and FSO versus object-store bucket behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmRenameKeys.java -->
