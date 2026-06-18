# sources/test-tools/syzkaller/tools/syz-hubtool/hubtool.go

Purpose: `syz-hubtool` uploads local reproducers and/or corpus programs to syz-hub and can drain reproducers from the hub for a manager.

Important APIs and flow: `main` parses target and hub credentials plus repro/corpus/workdir/drain flags, resolves `prog.Target`, expands workdir paths into crash repro glob and corpus DB path, loads repro programs with `loadProgs` and corpus DB with `loadCorpus`, connects with `rpctype.NewRPCClient`, obtains an auth token from `pkg/auth` when no key is supplied, calls `Hub.Connect` with corpus, optionally calls `Hub.Sync` with repros, and in drain mode loops `Hub.Sync` with `NeedRepros` until no data remains. `loadProgs` glob-expands, reads, deserializes, and deduplicates programs by raw bytes. `loadCorpus` reads a corpus DB and serializes each program.

State and persistence: no local writes. Persistent state changes happen remotely in syz-hub. It reads crash repro files and corpus DBs.

Dependencies and integration: uses syzkaller RPC types, auth token cache, corpus DB reader, target deserializer, and hub RPC methods.

Risks: missing hub address/client/manager is not validated before RPC. Dedup is byte-based before canonical serialization for repro files. Drain can run for a long time. Auth token retrieval depends on environment and HTTP client behavior.

Test signals: no direct test. Practical signal is successful Hub.Connect/Hub.Sync and hub-side corpus/repro counts.
