# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.hh

Purpose: declares a legacy mutable string class used across XRootD utility code as a C-string-compatible owned buffer with convenience operations.

Important APIs, types, and functions: the class exposes `c_str()`, `length()`, `capacity()`, indexed access, find/rfind, prefix/suffix checks, wildcard `matches()`, tokenization, resize/append/assign/insert/replace/erase/case/reset operations, assignment and concatenation operators, equality operators, digit/atoi helpers, and static block-size controls. `STR_NPOS` is `-1`.

Control flow: callers generally construct from a char pointer or empty capacity, mutate through append/insert/replace, and pass `c_str()` to older APIs. Optional `form()` methods provide printf-style formatting on non-Windows platforms.

State and persistence: private state is the owned char buffer, current length, capacity, and static allocation granularity. No persistence or synchronization is provided.

Dependencies and integration points: includes `XrdSysHeaders.hh` and C stdlib/stdio/varargs. Stream output operator and free `operator+` overloads integrate it with C++ stream and concatenation syntax.

Risks and test signals: many methods pass `XrdOucString` by value, creating extra copies and depending on correct copy semantics. `operator[]` aborts on invalid indexes. Tests should verify ABI, null-string handling, copy/assignment independence, and compatibility with functions expecting mutable C strings.
