## sources/distributed-fs/xrootd/src/Xrd/XrdPollInfo.hh

Purpose: defines the per-link poll attachment record shared between link objects and poll backends.

Important APIs/types/functions: fields include `Next` for poll queue chaining, immutable `Link` reference, backend `PollEnt`, owning `Poller`, fd number, `inQ`, `isEnabled`, and reserved flags. `Zorch()` resets the record to detached/disabled fd `-1`.

Control flow: `XrdLinkXeq` embeds `PollInfo`. `XrdLinkCtl::Alloc()` sets `FD`; `XrdLink::Activate()` attaches it to a poller; poll backends toggle `isEnabled` and queue state; close paths detach and reset state.

State/persistence: runtime-only attachment state. The `Link` reference is stable for the object lifetime.

Dependencies/integration: forward declares `XrdLink`, `XrdPoll`, and `pollfd`; used by every poll backend and link executor.

Risks: because `PollInfo` is embedded in reusable link objects, backends must not retain pointers after detach/reset. Queue flags must remain consistent to avoid double scheduling or missed events.

Test signals: attach/detach/reset tests should assert fd, poller, enabled, queue, and `PollEnt` transitions, especially under close while events are pending.
