# sources/distributed-fs/tahoe-lafs/src/allmydata/util/iputil.py

## Purpose

This module provides network utility helpers for local IPv4 discovery, TCP port allocation/listening, file descriptor limit increases, and safe endpoint adoption. It helps Tahoe/Foolscap bind listening ports while reducing port reuse races on POSIX.

## APIs and control flow

`increase_rlimits()` tries to raise `RLIMIT_NOFILE` where useful. `get_local_addresses_sync()` enumerates `netifaces` interfaces and IPv4 addresses. `_foolscapEndpointForPortNumber()` returns either a Foolscap endpoint string for a requested port or, for automatic POSIX allocation under an `IReactorSocket` reactor, binds/listens a socket, duplicates the fd, marks it nonblocking/close-on-exec, and returns a `CleanupEndpoint` wrapping `AdoptedStreamServerEndpoint`. `listenOnUnused()` calls `tub.listenOn()` and sets a localhost location.

`CleanupEndpoint` delegates `listen()` and closes the adopted fd on garbage collection if it was never listened on, coordinating with `gcutil.fileDescriptorResource`.

## State, dependencies, risks, and tests

State is OS sockets/file descriptors and resource limits. Dependencies include `netifaces`, Foolscap `allocate_tcp_port`, Twisted endpoint/reactor interfaces, POSIX `fcntl`, `resource`, local GC tracking, and attrs.

Risks include fd leaks if adoption/listen cleanup changes, race-prone fallback allocation on Windows or reactors without `IReactorSocket`, platform-specific rlimit behavior, and only IPv4 address enumeration. Test signals should cover local address enumeration, explicit and automatic ports, POSIX adopted fd cleanup, fallback allocation, tub integration, rlimit no-op/error paths, and close-on-exec/nonblocking flags.
