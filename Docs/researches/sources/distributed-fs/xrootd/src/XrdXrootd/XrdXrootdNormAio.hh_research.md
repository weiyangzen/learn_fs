# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.hh

Purpose: declares the normal asynchronous I/O task type used for standard xrootd reads and writes.

Important APIs/types/functions: `Alloc`, `DoIt`, `Read`, `Write`, `Recycle`, private `CopyF2L`, `CopyL2F`, `CopyF2L_Add2Q`, `Send`, and state fields `sendQ`, `sendOffset`, `reorders`, and `didSched`.

Control flow: the class overrides the `XrdXrootdAioTask` virtual hooks so the shared AIO task framework can call back for file-to-link and link-to-file movement.

State and persistence behavior: task objects are pooled and reset by `Init()`. No durable state is owned; writes persist through the underlying SFS file object.

Dependencies: `XrdXrootdAioTask`, forward declarations for AIO buffers and xrootd file objects.

Integration points: selected by protocol/file code for non-page-based asynchronous operations.

Risks: private constructor/destructor enforce factory/recycle ownership. Derived state must be fully reset on reuse; `didSched` is declared but the implementation primarily uses inherited `aioState` scheduling flags.

Test signals: factory reuse, virtual dispatch from base callbacks, state reset between read and write reuse, and destructor behavior when free-list overflows.
