<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SortedList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SortedList.java

Purpose: `SortedList` is a package-private list-like container optimized for many elements with comparatively few integer weights. It stores elements in a `TreeMap<Integer, List<E>>` so iteration and indexed access are ordered by weight.

Important APIs and types: Supported operations are `size`, `isEmpty`, `add(E, int weight)`, `get`, `remove(int)`, `contains`, `remove(Object)`, `removeAll`, `clear`, `iterator`, and `toString`. Most mutating and array/list-view methods from `List` throw `UnsupportedOperationException`.

Control flow: Adding an element appends it to the bucket for its weight. `get` and indexed `remove` walk buckets in ascending weight order while subtracting bucket sizes. Object removal scans buckets, removes empty buckets, and decrements the element count only when removal succeeds.

State and persistence behavior: State is in-memory only: a sorted bucket map plus a separate `numElements` counter. The class is explicitly not thread-safe.

Dependencies and integration points: It is a low-level utility for pipeline placement code where datanodes or candidates are weighted by current pipeline counts. Its `Class<E>` constructor argument protects `contains/remove` from matching unrelated object types.

Risks: It implements `List` but many standard operations are unsupported, so generic callers can fail at runtime. The custom iterator's `hasNext` only checks the current bucket iterator, so consumers must rely on standard next progression and avoid structural mutation during iteration. Empty-list handling for unsupported or index methods must be tested.

Test signals: Tests should verify sorted-by-weight iteration, stable bucket insertion order for equal weights, indexed get/remove, object removal and bucket cleanup, removeAll counts, type mismatch contains behavior, and expected unsupported operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SortedList.java -->
