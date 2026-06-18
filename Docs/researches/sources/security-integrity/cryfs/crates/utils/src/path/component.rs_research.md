# sources/security-integrity/cryfs/crates/utils/src/path/component.rs

Purpose: strict path component types for validated single components of absolute paths.

Important APIs/types/functions: borrowed `PathComponent` is a transparent `str` wrapper; owned `PathComponentBuf` stores `String`. APIs include `try_from_str`, `try_from_string`, `as_str`, conversions from/to `str`, `OsStr`, `String`, `OsString`, `Borrow`, `Deref`, `ToOwned`, and `FromStr`.

Control flow: constructors validate invariants: UTF-8, non-empty, no `/`, `\`, or null, and not `.` or `..`. Internal unchecked constructors are used after trusted validation by iterators.

State/persistence: stores or borrows component text only.

Dependencies/integration: used by rustfs APIs and `AbsolutePath` iteration to avoid invalid path names crossing filesystem layers.

Risks: uses unsafe transparent cast from `str` to `PathComponent`; soundness depends on `repr(transparent)` and invariant discipline. `.` and `..` map to `NotAbsolute`, which may be semantically surprising for component parsing.

Test signals: extensive tests cover valid conversions, invalid empty/dot/slash/backslash/null/non-UTF8 cases, special characters, Unicode, unchecked helpers, and owned/borrowed conversions.
