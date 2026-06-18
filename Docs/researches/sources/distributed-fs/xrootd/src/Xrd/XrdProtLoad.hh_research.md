## sources/distributed-fs/xrootd/src/Xrd/XrdProtLoad.hh

Purpose: declares the protocol-loader `XrdProtocol` implementation that temporarily owns new links while deciding which real protocol should handle them.

Important APIs/types/functions: public static `Load`, `Port`, `Statistics`, constants `ProtoMax` and `PortoMax`, and protocol overrides `Match`, `Process`, `Recycle`, and `Stats`. Private static helpers resolve protocol objects and ports. Static arrays `ProtName`, `Protocol`, and `ProtoCnt` hold loaded protocols; instance fields `myPort` and `myProt` hold per-port selection order.

Control flow: `XrdMain` creates an `XrdProtLoad` for each accept port. `Process()` then performs protocol matching and handoff.

State/persistence: process-global protocol registry and per-loader port mapping sequence. No durable storage.

Dependencies/integration: extends `XrdProtocol` and depends on `XrdProtocol_Config` during configuration.

Risks: `PortoMax` is declared but not used in this file set; actual port vector growth is controlled elsewhere by `ProtoMax` and memory. `Match()` always returns null because this object is not itself a selectable protocol.

Test signals: compile plugin API users, validate loader construction with no mappings, TLS marker ordering, and `Statistics()` behavior when no protocols are loaded.
