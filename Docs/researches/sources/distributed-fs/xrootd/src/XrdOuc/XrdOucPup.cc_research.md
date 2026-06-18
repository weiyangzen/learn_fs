<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.cc

Purpose: Implements compact pack/unpack helpers for length-prefixed strings, numeric values, and descriptor-driven structured messages.

APIs and control flow: Static `Pack()` overloads encode strings/binary blobs into `iovec` or contiguous buffers, always adding a network-order length for data blobs. Numeric `Pack()` uses a compact inline encoding when possible. Descriptor-driven `Pack()` walks `XrdOucPupArgs`, emits typed numeric values, strings, marker/skipped iovec entries, data/total lengths, and end-fill values. `Unpack()` reads length-prefixed data or descriptor-driven typed streams, respects `PT_Fence` optional boundaries, and writes pointers or converted integers into caller structures. `eMsg()` formats diagnostics by type and optional names.

State and persistence: The object stores optional error routing and names. Pack/unpack functions mutate caller buffers, iovec arrays, and target structures but do not persist data.

Dependencies and integration: Uses network byte order conversions, platform endian helpers, `iovec`, and `XrdSysError`. It supports XRootD internal protocol serialization.

Risks and test signals: Correct alignment of target structures is the caller's responsibility. Tests should cover every descriptor type, optional fences, too-long strings, iovec overflow, buffer overrun detection, endian conversion, null strings, and mismatch diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPup.cc -->
