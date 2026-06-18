## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.cc

Purpose: implements the transfer daemon coordinator. It ensures singleton daemon execution, starts transfer workers and migration scanning, starts request bosses, listens for UDP agent messages, and periodically wakes queues.

Important APIs and control flow: `Init()` acquires a unique lock file under `Config.QPath`, initializes `XrdFrmTransfer`, adjusts migration wait time, starts auto-migration when path and output command configuration allow it, and starts all four `XrdFrmReqBoss` instances. `Pong()` has two phases: first call creates a UDP socket at `xfrd.udp` and spawns a listener thread; re-entered thread attaches the socket to `XrdOucStream`, ignores list messages, handles wakeup pings by posting matching bosses, and delegates other messages to `XrdFrmXfrAgent::Process()`. `Start()` starts the ponger and loops waking every boss at `Config.WaitQChk`.

State and persistence: static bosses own persistent request files. The daemon lock file prevents duplicate daemons. UDP socket state is static inside `Pong()`.

Dependencies and integration: ties together `XrdFrmReqBoss`, `XrdFrmTransfer`, `XrdFrmMigrate`, `XrdFrmXfrAgent`, `XrdNetSocket`, and global configuration.

Risks and test signals: `Pong()` recursive/threaded initialization is compact and easy to break; tests should verify first-call socket setup, listener reentry, wakeup command parsing, duplicate daemon lock handling, migration disabled warnings, and periodic wakeups when UDP is silent.
