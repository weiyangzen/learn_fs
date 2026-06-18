# sources/user-network-fs/smblibrary/Utilities/Comparers/ReverseComparer.cs

Purpose: `ReverseComparer<T>` adapts an existing comparer to descending order.

Important APIs/types/functions: constructor stores an `IComparer<T>` and `Compare(x,y)` calls the wrapped comparer as `Compare(y,x)`.

Control flow: one delegated comparison with reversed operands.

State and persistence behavior: stores a comparer reference; no other state.

Dependencies and integration points: used by `KeyValuePairList.Sort` for descending key sort.

Risks: a null comparer causes `NullReferenceException`. Reversing operands can still overflow or violate ordering if the wrapped comparer is inconsistent.

Test signals: ascending versus descending sort tests and null-constructor behavior.
