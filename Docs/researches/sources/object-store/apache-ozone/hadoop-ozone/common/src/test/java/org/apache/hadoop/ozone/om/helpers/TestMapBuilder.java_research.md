# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestMapBuilder.java

Purpose: validates `MapBuilder`, a generic mutation-tracking map builder used to preserve unchanged metadata/tag maps.

Important APIs/types/functions: covers `MapBuilder.of`, `copyOf`, `put`, `putAll`, `remove`, `set`, `build`, `initialValue`, and `isChanged`.

Control flow and state: parameterized tests run over empty, one-entry, and two-entry immutable maps. Re-putting existing key/value pairs and removing missing keys are no-ops that return the initial map instance. Updating existing values, adding new keys, removing existing keys, or setting a different map marks changed.

Dependencies and integration points: uses Guava `ImmutableMap`, Java `HashMap` and `LinkedHashMap`. This behavior supports OM helper builders that want to avoid copying or persisting unchanged metadata.

Risks and test signals: catches incorrect dirty tracking, accidental loss of iteration order during removals, and returning mutable/new maps on no-op paths. `setImmutable` asserts immutable replacement can be preserved by identity.
