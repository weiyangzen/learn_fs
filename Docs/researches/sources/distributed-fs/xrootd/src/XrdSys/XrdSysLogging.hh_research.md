## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.hh

Purpose: declares the singleton-style logging plugin forwarding helper.

Important APIs/types/functions: `XrdSysLogging::Parms` carries `logfn`, `logpi`, `bufsz`, `keepV`, and `hiRes`; static `Configure(XrdSysLogger&, Parms&)` applies those settings; static `Forward(timeval, unsigned long, iovec*, int)` forwards a message. Private `MsgBuff` encodes async queue records with timestamp, thread id, next offset, buffer size in doublewords, and signed message length.

Control flow: users prepare `Parms`, call `Configure()`, then `XrdSysLogger::Put()` calls `Forward()` when global forwarding is enabled.

State and persistence: exposes static `lpiTID`, `lclOut`, and `rmtOut` declarations plus private static methods. Runtime queue state lives in the `.cc` file.

Dependencies and integration: includes `XrdSysLogPI.hh`, pthread wrappers, `sys/time.h`, and `sys/uio.h`. It sits between local logger and logging plugin ABI.

Risks: `MsgBuff` size limits cap messages at `SHRT_MAX` and queue records at the encoded doubleword size. Static output flags imply one process-wide logging configuration.

Test signals: parameter defaults, message length boundaries, struct layout assumptions, and integration with `XrdSysLogger::setForwarding`.
