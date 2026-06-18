# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.cc

Purpose: implements site-name normalization and exports the result as `XRDSITE`.

Important APIs, types, and functions: `XrdOucSiteName::Set()` duplicates the supplied name, truncates it to `maxlen`, replaces characters outside `[A-Za-z0-9_-:]` with `.`, exports it through `XrdOucEnv::Export()`, and returns the allocated string.

Control flow: null input becomes an empty string. Non-null input is copied before mutation. The function then walks each retained byte and sanitizes invalid characters.

State and persistence: the duplicated string is intentionally retained because `XrdOucEnv::Export()` installs it into the process environment. Persistent state is the process environment variable, not a file.

Dependencies and integration points: depends on `<cctype>`, `<cstring>`, `XrdOucEnv`, and the declaration header. It integrates with startup/configuration code that needs a bounded site label exposed to child processes and plugins.

Risks and test signals: `isalnum(site[i])` should ideally cast to unsigned char for non-ASCII bytes. Each call allocates a new string and returns a pointer that should not be freed after export. Tests should cover truncation, allowed punctuation, replacement behavior, null input, and environment visibility.
