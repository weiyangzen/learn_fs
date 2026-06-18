# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.hh

Purpose: declares BWM event logging, including the event payload shape and asynchronous delivery state.

Important APIs/types/functions: `XrdBwmLogger::Info` contains identity, LFN, local/remote nodes, arrival/begin/complete times, policy queue counts, transfer size/time, and flow direction. Public methods are `Event`, `Prog`, `sendEvents`, and `Start`.

Control flow: callers create a logger from a target string, call `Start`, then call `Event` when a request retires. Delivery is done by `sendEvents` in a background thread.

State and persistence: header exposes internal queue and free-list members, thread id, sink handles, EOL mode, and cap `maxmInQ = 256`. No disk persistence is guaranteed.

Dependencies and integration points: uses `XrdSysPthread` and forward-declares message/program/error classes. Used by `XrdBwmConfig` and `XrdBwmHandle`.

Risks: all event string fields are raw `const char *`; callers must keep them valid through formatting. Public `sendEvents` is thread entry API rather than an intended external control point.

Test signals: compile against handle/config, Info field mapping, target string preservation from `Prog`, and queue cap behavior.
