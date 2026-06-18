## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.hh

Purpose: declares the singleton transfer daemon facade and its four request bosses.

Important APIs/types: public static `Init()` performs daemon setup, `Pong()` manages UDP listener/wakeup messages, and `Start()` runs the daemon loop. Private `Boss()` maps an operation character to the proper `XrdFrmReqBoss`. Static `GetBoss`, `PutBoss`, `MigBoss`, and `StgBoss` represent request streams.

State and persistence: persistent queue state is delegated to the bosses; daemon identity is enforced in the implementation by a lock file.

Dependencies and integration: includes `XrdFrmReqBoss.hh`. The main executable calls this header's API when not running in agent mode.

Risks and test signals: static bosses mean queue personas are fixed at compile time. Tests should assert operation mapping for all request tokens and that daemon setup failure prevents `Start()` from running.
