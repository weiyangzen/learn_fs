## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.cc

Purpose: implements the external request-agent process mode. It reads textual requests from stdin, parses operation-specific fields, and forwards them to persistent `XrdFrcReqAgent` queues for stage, get, migrate, and put operations.

Important APIs and control flow: static agents are created for `getf`, `migr`, `pstg`, and `putf`. `Start()` initializes each agent against `Config.QPath`, attaches stdin to an `XrdOucStream`, and processes lines until EOF. `Process()` dispatches operations: `+` stage, `<` copy in, `>`/`=` copy out, `&`/`^` migrate, `-` cancel inbound/stage, `~` cancel outbound/migrate, `?` list, and `!` ping. `Add()` parses request ID, notify path, priority, mode, and one or more paths; it maps mode to options, handles opaque query offsets, validates URL or absolute path, and enqueues each request. `Del()` and `List()` handle cancellation and queue inspection.

State and persistence: request state is persisted by `XrdFrcReqAgent` under the queue path. The agent process itself only keeps static agent objects and the current parsed request.

Dependencies and integration: pairs with `XrdFrmXfrDaemon::Pong()` and `XrdFrmReqBoss` queue files. It uses `XrdFrcUtils` for URL/mode mapping and global `Config` for process identity/admin mode.

Risks and test signals: parsing is positional and mutates path tokens to strip opaque fields. Tests should cover multi-path requests, trace/user suffixes in op tokens, priority clamping, invalid URLs, cancel shorthand, list item filters, stdin EOF exit code, and unsupported operations.
