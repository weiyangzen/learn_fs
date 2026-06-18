# sources/test-tools/ior/src/aiori-LIBNFS.h

## Purpose
Defines the small public options structure used by the libnfs IOR backend.

## Important APIs, Types, and Functions
- Include guard `_AIORI_LIBNFS_H`.
- `libnfs_options_t` contains `char *url`, the RFC2224 NFS URL consumed by `LIBNFS_Initialize` in `aiori-LIBNFS.c`.

## Control Flow
This header has no executable control flow. It is included by the libnfs backend so option allocation and callback initialization share the same structure layout.

## State and Persistence
No state is stored in the header itself. The `url` pointer is runtime configuration owned by the allocated backend options object.

## Dependencies and Integration Points
Integrated directly with `aiori-LIBNFS.c` option parsing. It does not include other headers, so consumers must include required definitions separately.

## Risks and Edge Cases
- The struct has no ownership annotation for `url`; callers must know whether option parsing stores borrowed or allocated strings.
- The header does not declare backend functions, only options.

## Test Signals
Compile the libnfs backend and verify option allocation, initialization, and URL parsing use the same `libnfs_options_t` layout.
