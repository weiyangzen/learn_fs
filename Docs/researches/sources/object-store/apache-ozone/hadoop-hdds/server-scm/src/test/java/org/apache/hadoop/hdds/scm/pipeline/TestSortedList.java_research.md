# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSortedList.java

## Purpose
`TestSortedList` stress-tests the custom `SortedList` collection against a Java `ArrayList` sorted with `Collections.sort`. It verifies insertion ordering, removal behavior, identity-preserving iteration, and duplicate-removal semantics under randomized operations.

## Important APIs, Types, and Functions
- `SortedList.add(element, weight)`, `remove`, `iterator`, `size`, and `isEmpty` are exercised through `List` semantics.
- Nested `Element` implements `Comparable` by weight and unique value while `hashCode` intentionally returns only weight.
- Static helpers `add`, `remove`, `assertLists`, and `assertOrdering` compare `SortedList` to a reference list.

## Control Flow
The main test runs 2,000 random operations. It adds elements 60 percent of the time and removes from either the Java list or `SortedList` otherwise. After every mutation, it asserts both containers have the same size, same ordering, same element containment, and same object identity sequence.

## State and Persistence Behavior
State is in-memory only. The random static `id` and `Random` drive operation variety, and each inserted element has a stable weight/value ordering key.

## Dependencies and Integration Points
The test depends only on JUnit, AssertJ, Java collections, and `SortedList`. It is a low-level utility test for pipeline package internals.

## Risks and Edge Cases
The test catches ordering errors with duplicate weights, stale index removal, and equality/hash collisions because `hashCode` is not unique. Randomness is useful for coverage but can make failures non-reproducible because no seed is fixed.

## Test Signals
Strong signals include bidirectional removal checks and `assertSame` during iteration, which means `SortedList` must preserve the actual element objects, not equivalent replacements.
