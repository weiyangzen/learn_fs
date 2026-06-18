# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ResolvedBucket.java

Purpose: `ResolvedBucket` bundles the bucket requested by a client and the real bucket reached after resolving a bucket link. It lets request handlers preserve audit context while rewriting operations to the target volume and bucket.

Important APIs and types: Constructors accept requested names plus `OmBucketInfo`, explicit real names, or `Pair` values. Accessors expose requested and real volume/bucket names, owner, and `BucketLayout`. `update(OmKeyArgs)`, `update(KeyArgs)`, and `update(OzoneObj)` return rewritten objects when the bucket is a link. `isLink`, `isDangling`, and `audit` describe resolution state.

Control flow: The update methods are simple branch points: if requested and real names differ, clone the supplied argument through its builder and set real names; otherwise return the original object. Audit always records requested volume/bucket and adds source volume/bucket for links.

State and persistence behavior: The class is immutable after construction and persists nothing. It carries persistent metadata read from bucket records, including owner and layout, and can represent dangling links by storing null real names.

Dependencies and integration points: OM bucket-link resolution returns this type to key, ACL, prefix, and audit paths. It depends on `OmBucketInfo`, protobuf `KeyArgs`, `OmKeyArgs`, and `OzoneObjInfo`.

Risks and test signals: Callers must handle dangling links before invoking update methods that can set null real names. Tests should check regular buckets return the same object, links rewrite only volume/bucket fields, audit maps retain requested names, and dangling links are detectable without corrupting audit output.
