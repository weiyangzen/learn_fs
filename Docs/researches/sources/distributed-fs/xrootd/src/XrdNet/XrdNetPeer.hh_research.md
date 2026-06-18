# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPeer.hh

## Purpose
`XrdNetPeer.hh` defines the small peer descriptor used by `XrdNet` accept/connect paths and UDP message infrastructure to carry a file descriptor, network address, optional peer hostname, and optional datagram buffer.

## Important APIs, Types, and Functions
`XrdNetPeer` has public data members: `fd`, `Inet`, `InetName`, and `InetBuff`. The constructor initializes nullable pointers. The destructor frees `InetName` and recycles `InetBuff`.

## Control Flow and State
The type is a plain transfer container. Producers fill it during accepts or UDP setup, and consumers inspect it or pass it to helpers such as `XrdNetRefresh::Register()`. It owns only the hostname string and buffer pointer, not necessarily the socket descriptor.

## Dependencies and Integration Points
It includes `XrdNetBuffer.hh` and `XrdNetSockAddr.hh`. `XrdNet.cc` fills `XrdNetPeer` for accepts/connects; `XrdNetMsg.cc` uses it when registering refreshable UDP endpoints.

## Risks and Test Signals
Because members are public, ownership conventions must be respected. Tests should check destructor recycling, hostname duplication by producers, and no double-free when peers are copied or reused by higher layers.
