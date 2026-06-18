# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/util.py

## Purpose
This module contains small compatibility and utility helpers used across sepolgen: progress display, set helpers, locale-aware byte/string conversion, rich-comparison scaffolding, and `cmp` compatibility.

## Important APIs, Types, And Functions
`PY3`, `bytes_type`, and `string_type` abstract Python version differences. `ConsoleProgressBar` writes a fixed 0-100 scale and advances in 50 two-percent blocks through `start()` and `step()`. `set_to_list()` copies set-like containers into lists. `first(s, sorted=False)` returns one element, optionally sorted deterministically. `encode_input()` and `decode_input()` use `locale.getpreferredencoding()` with UTF-8 fallback on `UnicodeError`. `Comparison` implements rich comparison methods in terms of subclass `_compare()`. `cmp_to_key` is imported from `functools` on modern Python or locally implemented for Python 2.6. `cmp(first, second)` returns -1/0/1-style ordering.

## Control Flow
Callers use these helpers directly. `ConsoleProgressBar.step()` updates current progress, computes displayed blocks, caps at 50, writes new indicator characters, flushes, and terminates with a newline once complete. `Comparison` subclasses implement only `_compare`; Python operators delegate to it.

## State And Persistence Behavior
Only `ConsoleProgressBar` holds mutable state: current steps, displayed blocks, output handle, and done flag. Encoding helpers and comparison helpers are stateless. The module writes to the supplied output stream only.

## Dependencies And Integration Points
`matching.Match` inherits from `Comparison`; `output.sort_filter()` uses `cmp_to_key`, `cmp`, `set_to_list`, and `first`; `refparser.parse_headers()` uses `ConsoleProgressBar`; encoding helpers are available for CLI-facing modules.

## Risks And Edge Cases
`first()` is nondeterministic unless `sorted=True` and raises `IndexError` on empty input. Encoding helpers assume the input type has `.encode()` or `.decode()` as appropriate; passing bytes to `encode_input()` on Python 3 or str to `decode_input()` can fail differently. `ConsoleProgressBar` can overrun semantics if `steps` is zero and does not clamp `current`. `Comparison` leaves hashing behavior to subclasses.

## Test Signals
Tests should cover deterministic and nondeterministic first-element paths, empty containers, progress output at start/mid/completion, locale encoding fallback, decode fallback, comparison delegation for all operators, `cmp` ordering, and `cmp_to_key` sorting behavior.
