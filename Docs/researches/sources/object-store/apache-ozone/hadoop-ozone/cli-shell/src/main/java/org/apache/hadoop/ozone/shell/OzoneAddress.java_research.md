## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneAddress.java

Purpose: central URI parser, validator, object-address model, and client factory for Ozone shell commands.

Important APIs and control flow: constructors parse full or short Ozone URIs into volume, bucket, snapshot indicator, key, scheme, host, and port. `createClient` supports only `o3://`, rejects REST, resolves HA service IDs vs host:port vs config defaults, and handles multi-service ambiguity. `createClientForS3Commands` has separate service-ID logic for S3 commands. `ensureBucketAddress`, `ensureKeyAddress`, `ensurePrefixAddress`, `ensureSnapshotAddress`, `ensureVolumeAddress`, `ensureRootAddress`, and `ensureVolumeOrBucketAddress` validate address shape for command-specific converters. `toOzoneObj` maps the address to ACL resource types and store types.

State and dependencies: immutable-ish parsed address state with one mutable `isPrefix` marker. Depends on Ozone config keys, `OzoneClientFactory`, `OmUtils`, HTTP URI builder, and ACL object builders.

Risks and test signals: URI edge cases are high impact because all shell handlers rely on this class. Multi-HA default behavior and snapshot indicator parsing need broad tests outside this subset.
