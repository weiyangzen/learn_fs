# sources/security-integrity/cryfs/crates/utils/src/peekable.rs

Purpose: Adds a tiny readability extension to Rust `std::iter::Peekable` iterators: an `is_empty` method that checks whether more items remain without consuming an item.

Important APIs and types: The public trait is `PeekableExt` with `fn is_empty(&mut self) -> bool`. It is implemented for `Peekable<T>` where `T: Iterator`.

Control flow: `is_empty` calls `self.peek().is_none()`. Because `peek` may fill the peek cache, the method needs `&mut self`, but it leaves the next item available for later `next`.

State and persistence behavior: There is no persistence. Runtime state is only the standard `Peekable` internal cache; repeated calls may keep a peeked value cached but do not advance the iterator.

Dependencies and integration points: The module depends only on `std::iter::Peekable`. It is a utility for parser-style code where checking exhaustion reads better as `iter.is_empty()` than `iter.peek().is_none()`.

Risks: The trait name overlaps conceptually with collection `is_empty`, but the mutable receiver is required by `Peekable::peek`. It cannot be called on arbitrary iterators until they are converted to `peekable()`.

Test signals: Unit tests cover empty iterators, non-empty iterators, exhaustion after consuming all elements, repeated non-consuming checks, and preserving the first element after `is_empty`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/peekable.rs` completely for this pass (76 lines, 2027 bytes).
