# sources/distributed-fs/xrootd/src/XrdCl/XrdClInQueue.hh

## Purpose
`XrdClInQueue.hh` declares `InQueue`, a thread-safe registry that maps incoming XRootD response stream ids to interested message handlers.

## Important APIs, Types, And Functions
The public API includes `AddMessageHandler`, `AssignTimeout`, `GetHandlerForMessage`, `ReAddMessageHandler`, `RemoveMessageHandler`, `ReportStreamEvent`, `ReportTimeout`, and `HasUnsetTimeout`. Private `DiscardMessage` filters malformed or irrelevant messages and extracts the sid. The core state types are `HandlerAndExpire` and `HandlerMap`.

## Control Flow
The queue is populated when a request handler is waiting for a response. Socket/PostMaster code passes each incoming message to `GetHandlerForMessage`, receives a handler plus action flags, and then invokes the handler outside or according to transport logic. Timeout and stream events can be pushed to all registered handlers.

## State And Persistence Behavior
State is a recursive-mutex-protected map keyed by 16-bit stream id. Each entry stores a raw `MsgHandler *` and expiration timestamp. No ownership or durable persistence is implied.

## Dependencies And Integration Points
The header depends on `XrdSysPthread`, `map`, `memory`, `XrdClXRootDResponses`, and `XrdClPostMasterInterfaces`. It is part of the lower-level transport response routing path.

## Risks And Test Signals
Tests should verify handler ownership is external, unset timeouts are observable, re-add preserves expiration, and removing missing handlers is harmless. Because stream ids are 16-bit, collision/reuse behavior under high request concurrency should be covered at the transport level.
