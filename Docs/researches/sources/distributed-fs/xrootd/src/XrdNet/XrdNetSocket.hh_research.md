# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.hh

## Purpose
`XrdNetSocket.hh` declares the socket wrapper API used throughout XRootD server components.

## Important APIs, Types, and Functions
The class provides construction from an optional error router and optional attached FD, static `Create()` and `socketPath()`, instance `Open()`, `Accept()`, `Close()`, `Detach()`, `LastError()`, `Peername()`, `SockData()`, `SockName()`, `SockNum()`, and static socket tuning helpers.

## Control Flow and State
The wrapper is single-FD: open once, close or detach before reuse. Destruction calls `Close()`. Error reporting is either routed through `XrdSysError` or stored in `ErrCode`.

## Dependencies and Integration Points
It includes `XrdNetAddr.hh` and platform socket headers. Consumers include XrdNet accept/connect logic, CMS admin sockets, XrdOfs event FIFOs, and xrootd admin setup.

## Risks and Test Signals
The API mixes ownership transfer and automatic close, so tests should assert `Detach()` prevents destructor close. Header-level contracts around path/port/flags combinations should be covered by integration tests.
