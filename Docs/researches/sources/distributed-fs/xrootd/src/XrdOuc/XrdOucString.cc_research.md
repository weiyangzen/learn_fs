# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.cc

Purpose: implements `XrdOucString`, a lightweight mutable C-string wrapper with manual capacity management, substring search, wildcard matching, insertion, replacement, erasure, case conversion, formatting, tokenization, numeric parsing, and overloaded operators.

Important APIs, types, and functions: private `adjust()` normalizes ranges and `bufalloc()` manages `realloc()` with optional block sizing. Constructors, `assign()`, `setbuffer()`, and destructor manage ownership. Search methods implement `find()`/`rfind()`/`endswith()`/`matches()`. Modifiers include `keep()`, `insert()`, `replace()`, `erase()`, `lower()`, `upper()`, `hardreset()`, `reset()`, and `tokenize()`. Operators implement assignment, concatenation, equality, stream output, and numeric conversion helpers.

Control flow: most mutations compute an effective range, resize only when capacity is insufficient, then use `memmove`, `memcpy`, or `strncpy` to mutate the internal null-terminated buffer. Replacement handles shorter replacements from left to right and longer replacements from right to left to avoid overwriting source text. Formatting uses a growing `vsnprintf()` loop on non-Windows builds.

State and persistence: each object owns `str`, `len`, and `siz`; static `blksize` controls allocation granularity process-wide. There is no locking or persistence. `setbuffer()` transfers ownership of a malloc-compatible buffer into the object.

Dependencies and integration points: depends on `XrdOucString.hh`, C stdio/string/limits, and varargs formatting. It is used broadly where legacy code wants a lighter mutable string than `std::string` and is also used by `XrdOucStream` capture logic.

Risks and test signals: `replace()` rejects null `s2`, but `erase(const char*)` calls `replace(s, 0, ...)`, so erase-by-substring currently returns no removal. `reset()` can read before the buffer when `len` is zero. `bufalloc()` leaves the old pointer intact only if callers do not overwrite it after failed `realloc`; several callers assign directly. Tests should cover empty strings, failed/large allocation behavior where practical, insert at boundaries, replace shorter/equal/longer, erase substring, `reset()` on empty strings, wildcard matching, tokenization with empty tokens, and numeric parsing.
