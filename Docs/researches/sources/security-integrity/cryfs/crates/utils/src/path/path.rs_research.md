# sources/security-integrity/cryfs/crates/utils/src/path/path.rs

Purpose: Defines `AbsolutePath` and `AbsolutePathBuf`, CryFS UTF-8-only absolute path types that enforce normalized Unix-style path invariants stronger than `std::path::Path`. The borrowed `AbsolutePath` is a transparent wrapper over `str`; the owned `AbsolutePathBuf` stores a `String` and derefs back to the borrowed type.

Important APIs and types: `AbsolutePath::try_from_str`, `root`, `is_root`, `join`, `as_str`, `is_ancestor_of`, `iter`, `split_last`, and `AbsolutePathBuf::root`, `root_with_capacity`, `try_from_string`, `push`, `push_all` are the main surface. The module implements `TryFrom<&str>`, `TryFrom<&std::path::Path>`, `TryFrom<String>`, `TryFrom<std::path::PathBuf>`, `FromStr`, `Borrow`, `Deref`, `AsRef`, `From`, `ToOwned`, and `IntoIterator`. It depends on `PathComponent`, `ParsePathError`, and `ComponentIter`.

Control flow: Parsing special-cases `/`, then checks the first character for absolute-path syntax and iterates UTF-8 char indices looking for slash, backslash, and NUL. Every component between slashes is validated through `PathComponent::check_invariants_except_contains_slash_or_null`; that delegates rejection of empty, `.`, and `..` components. `join` builds a pre-sized root buffer, appends the existing path with `push_all`, appends one component, and asserts the expected length. `split_last` finds the final slash, handles the single-component root-parent case, and re-wraps parent and child with invariant assertions.

State and persistence behavior: There is no external persistence. State is the path string itself, and most conversions avoid allocation for borrowed paths by using `repr(transparent)` plus unsafe pointer casting after validation. Owned paths can be converted into `String` or `PathBuf`. `push` preserves invariants for valid components, while `push_all` can append another absolute path to a non-root base.

Dependencies and integration points: This file is part of the `cryfs_utils::path` module and is intended as a safer path carrier for filesystem-facing CryFS code. It integrates with Rust standard path conversions for OS boundaries but rejects non-UTF-8 paths. Component iteration is shared with the path iterator module.

Risks: `new_without_invariant_check` and `AbsolutePathBuf::new_without_invariant_check` are unsafe-by-convention escape hatches and must only be called after validation. `is_ancestor_of` deliberately treats a path as not its own ancestor and requires a slash boundary after the prefix. The `push_all_root_onto_path` test expects `/foo/`, which violates the documented no-trailing-slash invariant, so callers should not treat `push_all` as a general invariant-preserving composition operation when the appended path is root. Windows-style paths are intentionally rejected or treated as invalid format when backslashes appear.

Test signals: The in-file tests cover root handling, pushing, all conversion traits, non-UTF-8 OS paths, NUL and backslash rejection, double/trailing slash rejection, dot-dot and dot components, special UTF-8 characters, `split_last`, iterator output, `join`, `is_ancestor_of`, root capacity, and `push_all` behavior.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/path/path.rs` completely for this pass (1061 lines, 34847 bytes).
