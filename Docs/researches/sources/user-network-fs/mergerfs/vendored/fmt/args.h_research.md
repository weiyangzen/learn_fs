# sources/user-network-fs/mergerfs/vendored/fmt/args.h

## Purpose

This fmt header implements dynamic formatting argument storage. It lets callers build a runtime list of positional and named arguments that can later be converted to `fmt::basic_format_args<Context>` for type-erased APIs such as `vformat`.

## Important APIs, types, and functions

`detail::is_reference_wrapper` and `detail::unwrap` detect and unwrap `std::reference_wrapper` so callers can intentionally store references for supported types.

`detail::dynamic_arg_list` is a linked list of polymorphic nodes. Each `typed_node<T>` owns a copied value and the list is used for values whose storage must not relocate because `basic_format_arg` entries point to them.

`template<typename Context> class dynamic_format_arg_store` owns `data_`, `named_info_`, and `dynamic_args_`. It exposes `push_back` overloads for ordinary values, `std::reference_wrapper`, and `fmt::arg` named arguments; `clear`; `reserve`; `size`; and implicit conversion to `basic_format_args<Context>`.

The `need_copy<T>` trait determines whether a value must be copied into stable dynamic storage. Strings and custom types are copied unless passed as references; built-in scalar types and string views can fit directly into `basic_format_arg`.

## Control Flow

`push_back` checks `need_copy<T>::value`. Values needing stable storage are copied into `dynamic_args_`, and the resulting reference is converted into a `basic_format_arg`. Values not needing a copy are unwrapped and emplaced directly.

Named arguments reserve slot zero in `data_` for a `named_arg_value` table. `emplace_arg(named_arg)` inserts that sentinel when the first named argument arrives, appends the actual value, pushes name/id metadata, and updates `data_[0]`. A small unique_ptr guard rolls back the appended value if `named_info_` insertion throws.

## State and Persistence Behavior

The store owns all copied argument state until `clear` or destruction. `data_` must remain contiguous because `basic_format_args` references it. `dynamic_args_` is a linked list specifically to avoid relocation invalidating references held by `data_`. Named argument names are copied into dynamic storage before their `const char_type*` is recorded.

## Dependencies and Integration Points

It includes `<functional>`, `<memory>`, `<vector>`, and fmt `format.h`. It depends on fmt internals such as `mapped_type_constant`, `basic_format_arg`, `named_arg_info`, `named_arg`, `std_string_view`, and `fmt::arg`. It is the dynamic counterpart to compile-time `make_format_args`.

## Risks and Edge Cases

Lifetime rules are central. Passing a reference wrapper stores a live reference, so the caller must keep the referenced object alive. Built-in types and string views are always copied or stored directly, and the reference-wrapper overload statically rejects cases where referencing would not make sense. Named argument index math accounts for the hidden sentinel; off-by-one regressions would break lookup. Exception safety around named metadata is handled for the value append, but allocation failures must still preserve vector invariants.

## Test Signals

Tests should cover positional values, custom types, strings, string views, reference wrappers observing later mutation, named arguments, duplicate names handled by lower layers, `reserve`, `clear`, and conversion to `basic_format_args`. Exception-injection tests around named argument insertion would validate rollback behavior.
