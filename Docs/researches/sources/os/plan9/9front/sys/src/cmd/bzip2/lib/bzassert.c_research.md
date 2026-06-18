# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzassert.c

This file defines libbzip2’s hard assertion failure handler for stdio-enabled builds.

Behavior:
- `BZ2_bz__AssertH__fail` prints a detailed internal-error report to stderr.
- Includes the libbzip2 version string from `BZ2_bzlibVersion`.
- Exits with status 3.

Notable implementation details:
- Includes both core private headers and stdio-private headers.
- Message is upstream-style and requests bug reports to the original maintainer.

Risks and caveats:
- Assertion failure terminates the process; no recovery path.
