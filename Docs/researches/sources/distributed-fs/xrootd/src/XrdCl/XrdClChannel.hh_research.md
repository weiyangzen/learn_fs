# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.hh

## Purpose

This header declares `XrdCl::Channel`, the client-side communication channel between XRootD client code and a server endpoint. It is part of the PostMaster/Stream transport stack and owns the per-channel stream object, incoming queue, channel data object, tick generator hook, transport handler link, and synchronization needed to send messages and react to stream lifecycle events.

The ownership note is the most important documentation in the file. A channel is normally owned through a `std::shared_ptr` held by `PostMaster`; `Stream` and `AsyncSocketHandler` instances keep weak or temporary shared ownership during active connections; `PostMaster` also tracks non-owning raw channel pointers for finalization. The design is explicitly about safe lifetime across asynchronous socket handlers, redirect collapse, and global shutdown.

## Important APIs, types, and functions

`Channel(const URL&, Poller*, TransportHandler*, TaskManager*, JobManager*, const URL&)` constructs a channel for one server URL and its preferred URL. The object keeps non-owning pointers to `Poller`, `TransportHandler`, `TaskManager`, and `JobManager`, and owns `std::unique_ptr<Stream> pStream`.

`Send(Message*, MsgHandler*, bool stateful, time_t expires)` is the public async send entry point. It queues a protocol message and arranges for the caller's message handler to be notified when the message is sent or times out. The `stateful` flag makes physical stream disconnects visible as errors for operations that cannot silently recover.

`QueryTransport(uint16_t, AnyObject&)` forwards transport-specific queries. `RegisterEventHandler` and `RemoveEventHandler` attach `ChannelEventHandler` listeners. `Tick(time_t)` is the time-event hook used by the task/tick system. `ForceDisconnect` overloads cover ordinary forced disconnect, hush/suppressed notification disconnect, and internal stream-triggered disconnect with a known channel shared pointer and session id. `ForceReconnect`, `NbConnectedStrm`, and `SetOnDataConnectHandler` expose reconnection and data-stream state to higher-level copy and read paths.

`CanCollapse(const URL&)`, `DecFileInstCnt()`, `SetSelf(std::shared_ptr<Channel>&)`, and `Finalize()` are PostMaster integration points. `SetSelf` stores the weak self pointer used by socket handlers and stream callbacks; `Finalize` releases resources under the assumption that job, poller, and task managers have already stopped.

## Control flow

The header describes the channel as the middle layer between PostMaster and Stream. PostMaster creates and owns the shared channel, calls `SetSelf`, then clients submit messages through `Send`. The stream layer drives network I/O and channel events; channel-level handlers observe status changes and disconnect/reconnect decisions.

Timer flow enters through `Tick`, which likely drains timeouts in `pIncoming` and stream state. Disconnect flow can originate from external users via `ForceDisconnect`, from reconnect policy via `ForceReconnect`, or internally from a stream with the `ForceDisconnect(self, sess)` overload to avoid lifetime races while callbacks are in flight.

## State and persistence behavior

All state is in-memory transport state. There is no durable persistence. The main mutable members are the endpoint URLs, `pStream`, `pChannelData`, `pIncoming`, `pTickGenerator`, `pSelf`, and `pMutex`. The class coordinates asynchronous lifetime rather than storing file or application data.

`pSelf` is weak to avoid a channel/stream cycle. `pStream` is owned uniquely by the channel, while socket handlers may hold shared channel ownership until they close. Shutdown correctness depends on `Finalize` and force-disconnect paths not racing with in-flight socket callbacks.

## Dependencies and integration points

The header depends on `XrdClStatus`, `XrdClURL`, `XrdClPoller`, `XrdClInQueue`, `XrdClPostMasterInterfaces`, `XrdClAnyObject`, `XrdClTaskManager`, and `XrdSysPthread`. It forward-declares `Stream`, `JobManager`, `VirtualRedirector`, `TickGeneratorTask`, and `Job`.

Primary integration is with PostMaster for channel lookup and lifetime, Stream for actual message I/O, Poller for non-blocking socket events, TransportHandler for protocol details, TaskManager for ticking, and JobManager for callback jobs. `ClassicCopyJob` indirectly uses channel data-stream APIs through PostMaster when scaling parallel reads.

## Risks and edge cases

The lifetime model is delicate: raw non-owning channel pointers in PostMaster are valid only while finalization discipline is maintained, and weak self pointers require callers to lock shared ownership before async use. Redirect collapse can remove PostMaster ownership while socket handlers still hold the channel, so cleanup paths must tolerate channels no longer present in the primary map.

The class stores several non-owning manager pointers. `Finalize` documentation says those managers may already be stopped; implementation must therefore avoid queuing new work after finalization. Disconnect overloads also need consistent locking around `pStream` and `pIncoming` to avoid races with callbacks.

## Test signals

No direct test is included in this work item. Strong signals would come from connection/reconnect integration tests, PostMaster finalization tests, redirect-collapse tests, data-stream connection callbacks, and timeout/disconnect behavior under concurrent sends. Existing consumers such as `XrdClStream`, `XrdClPostMaster`, and copy data-stream scaling are the relevant integration surfaces.
