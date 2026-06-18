# sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.h

Purpose: Declares tester-server utilities exposed outside `TesterServer.cpp`.

Important APIs/types/functions: Declares `testDatabaseLiveness(Database cx, double databasePingDelay, std::string context, double startDelay = 0.0)` and `printSimulatedTopology()`.

Control flow: No header implementation. The declarations are used by the main test orchestrator for pre/post quiescence liveness checks and topology diagnostics.

State and persistence behavior: No header state. The declared liveness function performs repeated transaction pings; topology printing reads simulator process state.

Dependencies and integration points: Includes `fdbclient/NativeAPI.actor.h`. `testerServerCore` itself is declared in `include/fdbserver/tester/tester.h`, not this private header.

Risks: Minimal. Callers must understand `testDatabaseLiveness` is an infinite actor until cancelled or failed.

Test signals: Runtime traces from implementation; compile coverage ensures signature alignment.
