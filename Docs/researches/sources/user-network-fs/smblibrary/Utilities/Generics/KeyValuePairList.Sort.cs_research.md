# sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.Sort.cs

Purpose: this partial class adds key-based sorting helpers to `KeyValuePairList<TKey,TValue>`.

Important APIs/types/functions: `Sort()`, `Sort(ListSortDirection)`, `Sort(IComparer<TKey>, ListSortDirection)`, and `Sort(IComparer<TKey>)`.

Control flow: default sort uses `Comparer<TKey>.Default`; descending wraps the comparer with `ReverseComparer<TKey>`; final sorting delegates to `List<T>.Sort` with a comparison over pair keys.

State and persistence behavior: mutates the list in place.

Dependencies and integration points: depends on `ReverseComparer<T>`, `System.ComponentModel.ListSortDirection`, and the base partial `KeyValuePairList`.

Risks: key comparer exceptions propagate. Null keys may fail depending on comparer. Sort stability is not guaranteed.

Test signals: ascending/descending ordering, custom comparer behavior, duplicate keys, null key policy, and in-place mutation.
