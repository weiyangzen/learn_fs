# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTUtils.hh

Purpose: provides templated utility functions that cannot live in non-template `XrdOucUtils`, currently string splitting and case-insensitive map lookup.

Important APIs, types, and functions: `splitString(Container&, const std::string&, const std::string&)` appends non-empty delimited substrings via `emplace_back()`. `caseInsensitiveFind<T>()` scans a `std::map<std::string,T>` comparing each key lowercased against a caller-supplied lower-case search key.

Control flow: `splitString()` repeatedly calls `find()` from the current start position and skips empty tokens. `caseInsensitiveFind()` delegates to `std::find_if()` and `std::equal()` with a lowercase comparison lambda.

State and persistence: no state is stored. All output is written into caller-provided containers or returned iterators.

Dependencies and integration points: depends on `<string>`, `<map>`, and `<algorithm>`. It integrates with code using STL containers while preserving XRootD utility naming.

Risks and test signals: `splitString()` with an empty delimiter can loop incorrectly because `delimiter.size()` is zero. `caseInsensitiveFind()` uses `std::equal()` without checking equal string lengths, so a shorter search key can be treated as matching a longer map key depending on iterator range assumptions. Tests should cover empty delimiters, consecutive delimiters, missing/partial case-insensitive keys, and mixed-case maps.
