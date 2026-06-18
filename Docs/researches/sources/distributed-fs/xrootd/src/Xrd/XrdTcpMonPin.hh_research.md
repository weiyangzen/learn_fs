# sources/distributed-fs/xrootd/src/Xrd/XrdTcpMonPin.hh

## Purpose

`XrdTcpMonPin.hh` defines the TCP post-monitoring plugin interface used when an `XrdLink` connection is about to close. The file was read completely.

## Important APIs, Types, and Functions

The abstract class `XrdTcpMonPin` declares `Monitor(XrdNetAddrInfo&, LinkInfo&, int)`. `LinkInfo` carries trace identity, fd, connection seconds, bytes in, and bytes out. The comments specify that plugins should retrieve the g-stream object from environment key `TcpMon.gStream*` and that instances are obtained through `XrdOucPinObject`.

## Control Flow

There is no implementation control flow. Server link teardown code calls `Monitor()` with network and link summary data. Plugin creation is delegated to the plugin manager.

## State and Persistence Behavior

The interface owns no state. Implementations may emit monitoring records based on the passed snapshot and any environment-provided stream object.

## Dependencies and Integration Points

It forward-declares `XrdNetAddrInfo` and documents integration with `XrdOucPinObject`, `XrdXrootdGStream`, and `XrdVERSIONINFO`. This is an extension point rather than core server logic.

## Risks and Edge Cases

The `liLen` argument is the versioning guard for `LinkInfo`; plugins should validate it before reading newly added fields. Implementations must not assume fd remains usable after teardown begins. Missing environment g-stream should cause plugin load failure per comments.

## Test Signals

Plugin ABI tests should load a sample pin object, verify `getInstance()` behavior with and without the expected environment pointer, and call `Monitor()` with short and full `liLen` values.
