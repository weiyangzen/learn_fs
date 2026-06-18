## sources/distributed-fs/xrootd/src/XrdNet/XrdNetOpts.hh

Purpose: Defines shared bit flags and constants used by XrdNet and XrdNetSocket option handling.

Important APIs and definitions: Network flags include `XRDNET_NEWFD`, `SENDONLY`, `MULTREAD`, `NODNTRIM`, `DELAY`, `KEEPALIVE`, `NOCLOSEX`, `NOEMSG`, `NOLINGER`, `UDPSOCKET`, `FIFO`, `NORLKUP`, `USETLS`, and `SERVER`. Low-order-byte masks `XRDNET_BKLG` and `XRDNET_TOUT` encode backlog or timeout. Constants define default UDP buffer size, max backlog, and linger seconds.

Control flow: No runtime logic. Flags are ORed into bind, connect, accept, and socket setup calls.

State and persistence: None.

Dependencies and integration points: Included by `XrdNet`, `XrdNetSocket`, `XrdNetMsg`, and clients constructing network options.

Risks: Backlog and timeout share the same low-order byte and are interpreted according to server/client mode. Flags are preprocessor macros rather than scoped enum values, so accidental overlap or misuse is unchecked. Typos in comments can obscure operational meaning.

Test signals: Static assertions or compile checks for non-overlap of flag groups; integration tests for each option in socket setup paths.
