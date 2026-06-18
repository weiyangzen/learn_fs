# sources/distributed-fs/xrootd/src/XrdSec/XrdSecEntityPin.hh

## Purpose

`XrdSecEntityPin.hh` declares the post-authentication entity processing plugin interface.

## Important APIs, Types, And Functions

- Pure virtual `Process(XrdSecEntity &entity, XrdOucErrInfo &einfo)` inspects or decorates an authenticated entity and can fail authentication by returning false with error information.
- Comments describe stacking behavior and loading through `XrdOucPinObject<XrdSecEntityPin>` with file-level object `SecEntityPin`.

## Control Flow

After a security protocol authenticates an entity, configured post-processing plugins can be called to add attributes or reject the entity. Stacked plugins should generally be called and their result returned unless the current plugin rejects.

## State And Persistence

The interface owns no state. Implementations may attach state to `XrdSecEntity` attributes or internal plugin objects.

## Dependencies And Integration Points

It forward-declares `XrdOucErrInfo` and `XrdSecEntity` and integrates with XRootD plugin loading/versioning via `XrdOucPinObject` and `XrdVERSIONINFO`.

## Risks And Edge Cases

- A failing plugin causes the framework to try another authentication protocol if available, so rejection semantics affect protocol negotiation.
- Stacked plugin ordering and error propagation must be designed carefully.

## Test Signals

Plugin tests should load a concrete entity pin, verify successful decoration, verify failure messages in `XrdOucErrInfo`, and cover stacked plugin pass-through behavior.
