# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.hh

## Purpose
`XrdNetPMarkFF.hh` declares the Firefly-specific packet-marking handle type that extends `XrdNetPMark::Handle` with socket state, UDP reporting destinations, and lifecycle emission helpers.

## Important APIs, Types, and Functions
The public API is `Start(XrdNetAddrInfo&)`, `addHandle()` for optional chained ownership, the copy-from-handle constructor, and a virtual destructor. Private `sockStats` captures bytes received, bytes sent, and RTT split into milliseconds and microsecond remainder. Private helpers emit messages, format UTC timestamps, and query socket stats.

## Control Flow and State
The object is constructed with base experiment/activity/app state and a trace identity, started once against a connected socket, then destroyed to emit flow closure. It owns `mySad`, `xtraFH`, `oDest`, `ffHdr`, and `ffTail`.

## Dependencies and Integration Points
It includes `XrdNetPMark.hh` and forward-declares address and socket-address types. Only the PMark config backend should construct it, while protocols see it as a base `Handle`.

## Risks and Test Signals
Ownership is the main header-level risk: `addHandle()` transfers a raw pointer that the destructor deletes. Tests should verify start-before-destroy behavior, chained handle deletion, and safe cleanup when start partially fails.
