# sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.cs

Purpose: `KeyValuePairList<TKey,TValue>` is an ordered list of key/value pairs with convenience lookup and projection helpers.

Important APIs/types/functions: constructors, `ContainsKey`, `IndexOfKey`, `ValueOf`, `Add(key,value)`, `Keys`, `Values`, and a typed `GetRange`.

Control flow: key lookup scans linearly using `this[index].Key.Equals(key)`, value lookup returns the first match or `default(TValue)`, projections allocate new lists.

State and persistence behavior: inherits mutable `List<KeyValuePair<TKey,TValue>>`; ordering and duplicates are preserved.

Dependencies and integration points: sort behavior is supplied by `KeyValuePairList.Sort.cs`.

Risks: null keys cause `NullReferenceException` when `Equals` is called. Returning `default(TValue)` makes missing keys indistinguishable from stored default values. Duplicate keys are allowed and first-match semantics are implicit.

Test signals: duplicate key behavior, missing/default value ambiguity, null keys, range typing, and projection order.
