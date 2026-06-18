## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.cc

Purpose: implements local log routing, timestamping, capture, rotation, trimming, and midnight/signal/fifo handlers for `XrdSysLogger`.

Important APIs/types/functions: constructor honors `XrdSysLOGFILE`/`XrdOucLOGFILE`; `AddMsg()` queues rotation-time messages; `AtMidnight()` queues tasks; `Bind()` binds to a log file and starts a handler thread; `Capture()` redirects messages to `XrdOucTListFIFO`; `ParseKeep()` parses rotation keep policy; `Put()` writes `iovec` messages; `Time()`/`TimeStamp()` format timestamps; private `FifoMake`, `FifoWait`, `HandleLogRotateLock`, `RmLogRotateLock`, `putEmsg`, `ReBind`, `Trim`, and `zHandler` implement log lifecycle.

Control flow: `Put()` gets time/thread id, optionally forwards through `XrdSysLogging`, prefixes timestamp when `iov[0].iov_base` is null, locks, captures or `writev`s. `Bind()` tears down conflicting handler mode, opens/rebinds the log file, creates rotation lock/fifo/signal handling, then starts `zHandler()`. `zHandler()` waits for fifo input, midnight, or signal, reopens/rotates logs, emits queued messages, and launches midnight tasks.

State and persistence: object state includes file descriptors, base fd, log path, suffix, keep policy, fifo path, rotation thread id, queued messages/tasks, and mutex. It creates log files, rotated date-suffixed files, fifo files, and `.lock` files.

Dependencies and integration: uses `XrdSysFD`, `XrdSysLogging`, `XrdSysTimer`, `XrdSysUtils`, `XrdSysThread`, `XrdSysE2T`, POSIX filesystem/signal APIs, and `XrdOucTListFIFO`.

Risks: partial `writev` is explicitly ignored. Handler thread is killed when rebinding. Rotation lock path handling has pointer arithmetic assumptions. Global capture pointer is shared across logger instances. Destructor removes lock but does not visibly stop handler thread.

Test signals: timestamp formats, env log binding, file/fifo/signal rotation, keep-by-count and keep-by-size trimming, capture mode, forwarding suppression, lock-file creation/removal, and write errors/partial writes.
