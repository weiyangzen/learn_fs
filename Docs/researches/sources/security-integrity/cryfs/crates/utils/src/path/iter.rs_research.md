# sources/security-integrity/cryfs/crates/utils/src/path/iter.rs

Purpose: iterator over components of a validated `AbsolutePath`.

Important APIs/types/functions: `ComponentIter<'a> { path: &'a str }`; implements `Iterator`, `DoubleEndedIterator`, `FusedIterator`, and `ExactSizeIterator`.

Control flow: `new` strips the leading slash. `next` splits on first slash; `next_back` splits on last slash; both use `PathComponent::new_assert_invariants` because the source absolute path should already be valid. `size_hint`, `count`, and `last` are specialized.

State/persistence: iterator mutates its remaining string slice only.

Dependencies/integration: returned by `AbsolutePath::iter()` and feeds filesystem path traversal code.

Risks: relies on `AbsolutePath` invariants to avoid panics in `new_assert_invariants`. Double-ended iteration logic assumes no empty components.

Test signals: parameterized tests cover root, one/multiple components, Unicode, forward/backward iteration, len/count/size_hint, next, next_back, last, and fused behavior.
