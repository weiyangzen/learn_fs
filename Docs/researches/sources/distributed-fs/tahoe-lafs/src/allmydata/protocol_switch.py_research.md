# sources/distributed-fs/tahoe-lafs/src/allmydata/protocol_switch.py

## Purpose
Allows one listening port to serve both legacy Foolscap negotiation and the newer HTTPS storage protocol. This supports automatic HTTPS availability after upgrade without requiring users to configure a second port.

## APIs, Types, And Control Flow
`create_tub_with_https_support(**kwargs)` creates a Foolscap `Tub`, defines a per-Tub subclass of `_FoolscapOrHttps`, and installs it as `tub.negotiationClass`. `_FoolscapOrHttps` starts as a Twisted `Protocol`, buffers the first bytes, and chooses protocol mode: buffers beginning with `GET /id/` are converted into Foolscap `Negotiation`; all other traffic is passed into a TLS-wrapped Twisted Web `Site`. `add_storage_server(storage_server, swissnum)` configures HTTPS serving with the Tub certificate, builds NURLs from TCP/Tor location hints, and intentionally skips I2P until HTTP client support exists.

## State, Persistence, And Integration
State lives in class attributes on the per-Tub protocol subclass: the owning `Tub` and configured `https_factory`. No files are written. It integrates with Foolscap internals through a metaclass that makes wrapper instances pass `isinstance(..., Negotiation)` checks, Twisted TLS/Web protocol machinery, `storage.http_server.HTTPServer`, `build_nurl`, and `StorageServer`.

## Risks And Test Signals
Risks include brittle byte-level protocol detection, the 30-second abort timer, dynamic `__class__` and `__dict__` mutation, incorrect factory protocol bookkeeping, unsupported/compound location hint formats, and assertion failures for malformed Tor hints. Test signals are `allmydata/test/test_protocol_switch.py`, storage HTTPS tests, and integration tests that exercise mixed Foolscap/HTTPS storage access on upgraded nodes.
