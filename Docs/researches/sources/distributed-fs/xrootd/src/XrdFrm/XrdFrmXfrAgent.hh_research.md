## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.hh

Purpose: declares the request-agent facade used by non-daemon `frm_xfr*` personas to translate command input into request queue operations.

Important APIs/types: public static `Start()` runs the stdin loop and `Process()` handles one parsed stream command. Private helpers `Add()`, `Del()`, `List()`, and `Agent()` map operation tokens to one of four static `XrdFrcReqAgent` instances.

State and persistence: the header declares static agents for get, put, migrate, and stage; durable request persistence is owned by those agent objects.

Dependencies and integration: includes `XrdFrcReqAgent.hh` and forward declares `XrdOucStream`. The daemon can also reuse `Process()` to handle UDP agent messages.

Risks and test signals: because all agents are static, repeated `Start()` calls in the same process are not isolated. Tests should verify operation-to-agent mapping and initialization failure propagation.
