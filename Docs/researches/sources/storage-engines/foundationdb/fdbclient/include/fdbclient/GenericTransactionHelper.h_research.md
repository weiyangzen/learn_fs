# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericTransactionHelper.h

Purpose: Provides a small template trait for retrieving the future type associated with a transaction type, pointer to transaction type, or `Reference<Transaction>` wrapper.

Important APIs/types/functions: Primary template `transaction_future_type<Transaction, T>` aliases `Transaction::FutureT<T>`. Specializations for `Transaction*` and `Reference<Transaction>` recursively resolve to the underlying transaction's future type.

Control flow: Generic templated code can use `typename transaction_future_type<Tr, RangeResult>::type` without caring whether it received a transaction object type, pointer, or Flow `Reference`.

State and persistence behavior: No runtime or persistent state; compile-time type selection only.

Dependencies and integration points: Depends on `flow/FastRef.h` for `Reference`. Supports generic management/transaction helpers and other template code that abstracts over native and external client transaction handles.

Risks: The trait assumes the underlying type exposes `template FutureT<T>`. Missing aliases fail at compile time. Additional smart-pointer wrappers require more specializations.

Test signals: Compile-only tests for raw transaction type, pointer, and `Reference`; use in generic functions returning futures for several payload types.
