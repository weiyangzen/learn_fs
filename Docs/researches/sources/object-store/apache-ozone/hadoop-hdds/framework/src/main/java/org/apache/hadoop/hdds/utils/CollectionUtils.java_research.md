# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CollectionUtils.java

Purpose: `CollectionUtils` provides static helpers for immutable map construction, flattening iterators, and top-N selection.

Important APIs/types/functions: `newUnmodifiableMap(values, getKey, existing)` merges values into a copy of an existing map and rejects duplicate keys. `newUnmodifiableMultiMap(values, getKey)` groups values by key and wraps both outer map and inner lists. `newIterator(Collection<List<T>>)` lazily flattens a collection of lists. `findTopN()` overloads keep the largest N items by natural order or comparator with optional filter.

Control flow: map helpers iterate all values and build new collections before wrapping. Flattening iterator advances through inner lists only when needed. Top-N maintains a min-heap of at most N accepted items, then drains it into reverse order so the result is descending by comparator.

State and persistence: stateless utility interface with static methods. Returned maps/lists are unmodifiable views/copies; contained objects remain mutable if their types are mutable.

Dependencies/integration: used across HDDS/Ozone code for collection transformations. Depends only on Java collections and functional interfaces.

Risks: `findTopN()` with `n <= 0` still adds then immediately polls, returning empty but doing work; null comparator/filter inputs are not guarded. Duplicate key error only reports previous value class, not new value details. Multi-map uses `Collectors.toMap` without merge function but keys are unique at that stage.

Test signals: `TestCollectionUtils` covers map duplicate rejection, flattened iteration, top-N ordering, limits, comparators, and filters.
