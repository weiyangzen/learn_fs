# sources/distributed-fs/xrootd/src/XrdCl/XrdClInQueue.cc

## Purpose
`XrdClInQueue.cc` implements the synchronized incoming-message handler registry used by the PostMaster/socket layer to route server responses to the correct `MsgHandler` by stream id.

## Important APIs, Types, And Functions
`DiscardMessage` validates that a message has at least an XRootD response header, ignores async attention messages (`kXR_attn`), and extracts the stream id from the response header. `AddMessageHandler` stores a handler with unset expiration. `GetHandlerForMessage` finds the matching handler, asks it to `Examine` the message, assigns expiration on first match, returns action and expiration, and removes the handler if requested. `ReAddMessageHandler`, `RemoveMessageHandler`, `ReportStreamEvent`, `ReportTimeout`, `AssignTimeout`, and `HasUnsetTimeout` manage lifecycle and timeout behavior.

## Control Flow
Handlers are indexed by `handler->GetSid()`. Incoming messages are discarded or matched by sid. A matched handler decides through `Examine` whether it should remain registered. Stream events and timeouts iterate the handler map, calling `OnStreamEvent`; handlers that return `RemoveHandler` are erased.

## State And Persistence Behavior
The queue stores `std::map<uint16_t, std::pair<MsgHandler *, time_t>>`, protected by `XrdSysRecMutex`. Expiration `0` means the associated request is still being sent or has not yet had timeout assigned. No message backlog is stored in this implementation despite the `rmMsg` parameter in `AddMessageHandler`.

## Dependencies And Integration Points
It depends on protocol response layout from `XProtocol`, `Message`, `MsgHandler`, logging, default environment, and status constants. The socket handler extracts async responses earlier, leaving this queue focused on normal responses.

## Risks And Test Signals
Important tests include sid endian extraction, attention-message discard, handler removal during iteration, timeout assignment before and after first response, stream-error broadcasting, and race scenarios where send completion assigns timeout after handler insertion. The unused `rmMsg` output suggests legacy behavior; callers should not rely on it being set here.
