# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/RadixNode.java

Purpose: Node wrapper for a slash-delimited prefix radix tree used by Ozone ACL prefix path lookup.

Important APIs and types: Stores node name, child map, and optional generic value. Methods are constructor, `getName`, `hasChildren`, `getChildren`, `setValue`, and `getValue`.

Control flow: Constructor initializes an empty `HashMap`. `hasChildren` currently returns `children.isEmpty()`, so despite its name it is true when the node has no children.

State and persistence behavior: In-memory tree node only; no persistence. Values can hold ACL or other metadata in `RadixTree`.

Dependencies and integration points: Used directly by `RadixTree`.

Risks: `hasChildren` is semantically inverted by name, and `RadixTree` relies on it as "is leaf/has no children". Raw `HashMap<String, RadixNode>` loses generic type safety and can produce unchecked warnings.

Test signals: Node construction, value set/get, child map mutation, and explicit coverage of `hasChildren` behavior to avoid accidental semantic changes.
