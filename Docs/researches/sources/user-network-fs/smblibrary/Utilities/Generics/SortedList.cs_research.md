# sources/user-network-fs/smblibrary/Utilities/Generics/SortedList.cs

Purpose: `SortedList<T>` is a custom sorted collection that inserts each item into a list at binary-search position.

Important APIs/types/functions: constructors with default/custom comparer, `Add`, `Contains`, `IndexOf`, `Remove`, `RemoveAt`, `CopyTo`, `Clear`, indexer, enumerators, `Count`, `IsReadOnly`, and static `FirstIndexOf`/`FindIndexForSortedInsert` overloads.

Control flow: `Add` finds an insertion index and inserts into the backing list. `FirstIndexOf` finds a candidate insertion point, checks equality, then walks backward to the first duplicate. `FindIndexForSortedInsert` performs a binary search and returns either an equal middle index or before/after the lower bound.

State and persistence behavior: stores sorted items in an in-memory `List<T>`.

Dependencies and integration points: generic utility; no persistence.

Risks: insertion is O(n) after O(log n) search. Returning an arbitrary equal index from insert means duplicate insertion order is not stable. Not thread-safe. Custom comparer inconsistency can break ordering.

Test signals: sorted insertion, duplicate handling, first-index lookup, custom comparer, removal, enumeration order, and empty/singleton edge cases.
