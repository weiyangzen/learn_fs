# sources/distributed-fs/xrootd/src/XrdCl/XrdClOptional.hh

## Purpose

This header implements a small pre-`std::optional`-style `Optional<T>` plus a `none` sentinel for APIs that need optional values without depending on newer standard library facilities.

## Important APIs, Types, And Functions

`None` and global `none` represent an empty value. `Optional<T>` provides construction from `T`, construction from `None`, copy/move constructors, destructor, copy/move assignment, boolean conversion, and dereference operators. It uses a union `Storage` to reserve aligned memory without always constructing `T`.

## Control Flow

Constructing from `T` placement-news a value and sets `optional` to false. Constructing from `none` leaves storage uninitialized and sets `optional` to true. Copy/move constructors construct a value only when the source has one. Dereference returns `memory.value`.

## State And Persistence

Each instance stores a boolean flag and in-place storage for `T`. There is no persistence outside object lifetime.

## Dependencies And Integration Points

It uses `<utility>` for move operations. It can be used anywhere in XrdCl needing lightweight optional values.

## Risks

The boolean naming is inverted and the destructor appears wrong: `~Optional()` calls `memory.value.~T()` when `optional` is true, which is the empty state, and skips destruction when a value exists. That can destroy uninitialized storage for empty optionals and leak resources for populated optionals. Copy/move assignment also does not construct or destroy when transitioning between empty and populated states, so non-trivial `T` types are unsafe. Boolean conversion returns `optional`, meaning it is true when empty, opposite of `std::optional`.

## Test Signals

Tests should use a non-trivial tracking type to verify construction/destruction counts for empty and populated optionals, transitions through copy/move assignment, boolean semantics, dereference only when populated, and sanitizer coverage for uninitialized destruction.
