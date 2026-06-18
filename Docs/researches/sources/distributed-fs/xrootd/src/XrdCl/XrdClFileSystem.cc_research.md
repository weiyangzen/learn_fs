# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileSystem.cc

## Purpose
`XrdClFileSystem.cc` implements the callback-oriented `XrdCl::FileSystem` client API for XRootD filesystem requests. It converts high-level operations such as locate, stat, directory listing, prepare, and extended-attribute operations into XRootD protocol messages, sends them through `MessageUtils::SendMessage`, and adapts responses back to `ResponseHandler` or synchronous wait helpers. It also owns filesystem-level URL state, load-balancer discovery, redirect behavior, local-file fallbacks, plugin dispatch, and several higher-order response handlers for recursive locate and directory-list workflows.

## Important APIs, Types, And Functions
The main exported implementation is `FileSystem`, backed by `FileSystemImpl` and shared `FileSystemData`. `FileSystemData::Send` wraps a user handler in `AssignLastURLHandler` and optionally `AssignLBHandler`, stamps `followRedirects`, and sends the protocol message. `AssignLoadBalancer` and `AssignLastURL` persist the best routing URL and most recent response URL under a mutex.

The anonymous namespace supplies support handlers. `LocalFS` handles local `Stat` and `Rm` with POSIX `stat` and `unlink`, then queues responses through the `JobManager` unless the handler is synchronous. `FilterXrdClCgi` strips client-private `xrdcl.*` CGI parameters before protocol submission. `DeepLocateHandler` expands manager responses into recursive locate requests and returns either combined disk-server locations, `suPartial`, or a not-found error. `DirListStatHandler`, `RecursiveDirListHandler`, and `MergeDirListHandler` implement stat enrichment, recursive traversal, chunked recursive reporting, and duplicate merging.

Every public async operation follows the same broad pattern: check `pPlugIn`, build a specific `Client*Request`, fill request id/options/dlen/body, process timeout parameters, set a transport description, and call `FileSystemData::Send`. Sync overloads create `SyncResponseHandler`, call the async variant, and then use `MessageUtils::WaitForStatus` or `WaitForResponse`.

## Control Flow
Construction optionally asks `PlugInManager` for a URL-specific `FileSystemPlugIn`; non-plugin instances register with `ForkHandler`. Destruction unregisters and releases the plugin and pimpl. Normal remote operations flow through `FileSystemData::Send`, where load-balancer assignment is deferred until the first successful response carrying a load-balancer host.

`DirList` is the most complex path. Async listing handles zip mode by statting first and delegating to `ZipListHandler`, translates flags into `kXR_dstat` and `kXR_dcksm`, wraps recursive and merge handlers as requested, and marks chunked responses in send parameters. Sync listing rejects chunked mode, auto-enables zip for `.zip`, optionally performs deep locate to query all disk servers, merges results, and otherwise waits on the async path. If stat was requested but the server did not return stat objects, it launches bounded concurrent `Stat` calls via `RequestSync`.

Extended attributes share `XAttrOperationImpl`, which creates a `kXR_fattr` request, fills subcode/options/attribute count, delegates body serialization to `MessageUtils::CreateXAttrBody`, and sends it. Single-value operation adapters in `XrdClFileSystemOperations.hh` later wrap/unpack these vector responses.

## State And Persistence Behavior
Persistent in-memory state is `pFollowRedirects`, `pUrl`, `pLastUrl`, and `pLoadBalancerLookupDone`; all routing mutations are mutex-protected. `FollowRedirects` can be toggled through `SetProperty`, and `LastURL` can be read through `GetProperty` after a successful response. No disk persistence is performed. Handler objects transfer ownership of statuses, responses, directory-list entries, and temporary `FileSystem` objects carefully, often deleting themselves on final response. Recursive handlers maintain outstanding counters and expiry timestamps across asynchronous callbacks.

## Dependencies And Integration Points
The file integrates with `DefaultEnv`, `PostMaster`, `JobManager`, `ForkHandler`, `PlugInManager`, `MessageUtils`, `XRootDTransport`, `RequestSync`, `ZipListHandler`, protocol structs from `XProtocol`, response types from `XrdClXRootDResponses`, and POSIX filesystem calls for local-file URLs. It is also the runtime backend used by the operation-template API in `XrdClFileSystemOperations.hh`.

## Risks And Test Signals
High-risk areas are callback ownership, self-deleting handlers, partial/chunked responses, recursive directory traversal, timeout arithmetic, and mutation of shared routing state while requests are in flight. `DeepLocateHandler` uses a `uint16_t` outstanding counter and explicitly checks overflow. `Prepare` erases the final newline without checking for an empty file list, so tests should cover empty input. `FilterXrdClCgi` should be tested against mixed public and `xrdcl.*` CGI parameters because an off-by-one substring calculation would corrupt opaque data. Integration tests should cover plugin and non-plugin paths, local stat/rm, redirect-disabled mode, load-balancer assignment, sync and async overload parity, directory-list flags including `Locate`, `Merge`, `Recursive`, `Chunked`, `Zip`, and `Cksm`, and xattr success/error vectors.
