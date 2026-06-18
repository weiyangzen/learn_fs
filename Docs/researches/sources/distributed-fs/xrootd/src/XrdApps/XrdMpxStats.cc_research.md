# sources/distributed-fs/xrootd/src/XrdApps/XrdMpxStats.cc

Purpose: implements the `mpxstats` UDP listener utility. It receives XML statistics datagrams on a configured UDP port and writes them to stdout either as raw XML or after conversion through `XrdMpxXml` into CGI/flat text formats.

Important APIs/types/functions: namespace globals `XrdMpx::Logger`, `Say`, `Opts`, and `statsQ`; `XrdMpxOut::statsBuff` holds source address, data length, and an 8190-byte payload; `XrdMpxOut::getBuff`, `Add`, and `Run` implement a small producer/consumer queue; `mainOutput` is the thread trampoline; `main` parses `-d`, `-f`, `-p`, and `-s`.

Control flow: `main` validates the port, blocks SIGPIPE/SIGCHLD, sets XrdSys thread stack size, opens a UDP server socket with `XrdNetSocket`, optionally creates an `XrdMpxXml`, starts one output thread, and then loops forever calling `recvfrom`. Received buffers are queued to `XrdMpxOut::Run`, which formats with sender host when `-s` is set and writes all bytes to stdout with EINTR retry.

State and persistence: all state is in memory. The output queue keeps input and free buffer linked lists under `XrdSysMutex` and wakes the consumer via `XrdSysSemaphore`; no data is persisted beyond stdout.

Dependencies and integration points: depends on XRootD networking (`XrdNetSocket`, `XrdNetAddr`), system threading/semaphores, and `XrdMpxXml`. It is an external utility consuming statistics multicast/unicast streams emitted by XRootD servers or collectors.

Risks: `fromLen` is initialized with `sizeof(sbP->From)` while `sbP` is null; this works only because `sizeof` is compile-time but is visually fragile. The write loop subtracts `rc` without handling `write` returning `-1` for non-EINTR errors, which can corrupt pointer/length arithmetic. Output buffer sizing assumes formatted output fits `sizeof(statsBuff)*2`.

Test signals: exercise option parsing, invalid port handling, raw/XML/flat/CGI output, sender host resolution, EINTR write retry, and high-rate UDP receive with queue reuse.
