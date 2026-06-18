## sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.hh

### Purpose
This header declares the configuration and path-mapping service for digFS.

### Important APIs, Types, and Functions
- `Configure` initializes digFS from a config file and parameter string.
- `pType` classifies expected logical path type as any, directory, or file.
- `GenAccess` fills a top-level access list for a client.
- `GenPath` maps a logical dig path and operation name to a real filesystem path and errno-style result.
- `GetLocResp` and `StatRoot` support locate and stat operations.
- Private helpers implement config parsing, audit logging, path export, proc validation, and directives.

### Control Flow
Consumers call `Configure` once, then call `GenAccess` for root directory listing or `GenPath` for concrete operations. Private parser methods are invoked only during configuration.

### State and Persistence
The class stores path-template and locate-response heap strings, response lengths, and grant/deny logging flags. It has no explicit destructor cleanup, consistent with global process-lifetime use.

### Dependencies and Integration Points
Forward declarations reduce header coupling to XrdOuc, XrdSec, and POSIX `stat`. `XrdDigFS.cc` consumes the public methods and `XrdDigConfig.cc` implements the private configuration grammar.

### Risks and Edge Cases
The public `GenPath` returns a `char *` that callers must `free`. The class is not obviously thread-safe internally; safety depends on configuration being immutable after startup and authorization using its own mutex. `locRlen*` are `short`, so response lengths assume small locate strings.

### Test Signals
Compile tests should ensure the `pType` enum remains aligned with `GenPath` logic. Runtime tests should assert `GenPath` ownership and error codes for unauthorized, invalid-prefix, too-long, file, and directory paths.
