# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/MapBuilder.java

Purpose: Copy-on-write builder for immutable maps, used for metadata and tags.

Important APIs/types/functions: Static constructors `empty`, `of`, and `copyOf` seed an immutable original. `put`, `putAll`, `remove`, `set`, `isChanged`, and `build` manage mutations. `initialValue` exposes the original within the package.

Control flow and state: `updated` is a `LinkedHashMap` created lazily. `build` returns the original immutable map if no change is recorded. `set` assumes reference inequality means change rather than deep equality.

State and persistence behavior: No direct persistence, but it builds maps that later serialize through `KeyValueUtil` into OM protobuf metadata/tag fields.

Dependencies and integration points: Used in `WithMetadata` descendants and request/metadata builders.

Risks: `put` marks changed with reference comparison (`prev != value`), so replacing an equal distinct value is still a change and replacing the same object is not. `set` can accept an immutable map, but later mutation requires modifiability. Not thread-safe.

Test signals: No-change identity, insertion order preservation, put/remove/set behavior, null rejection, and immutable build output.
