# sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.cc

## Purpose

This file implements central helpers for sending, redirecting, rewriting, and constructing XRootD messages. It is the bridge between prepared `Message` buffers, stream ID management, `XRootDMsgHandler`, `PostMaster`, redirector registry, timeout defaults, CGI rewriting, and xattr protocol body encoding.

## Important APIs, Types, And Functions

`MessageUtils::SendMessage` allocates a stream ID, handles checkpoint embedded stream IDs, marshals the request, configures an `XRootDMsgHandler`, attaches host/load-balancer/chunk/kernel-buffer/CRC state, and calls `PostMaster::Send`. `RedirectMessage` registers a virtual redirector, marshals the request, configures a redirect-aware message handler, and calls `PostMaster::Redirect`.

`ProcessSendParams` fills default request timeout, expiry, and redirect limit from `DefaultEnv`. `RewriteCGIAndPath` updates path-bearing request bodies after redirects. `MergeCGI` merges parameter maps with replace-or-append semantics. The two `CreateXAttrVec` overloads encode xattr name/value vectors while enforcing protocol limits.

## Control Flow

Normal send flow obtains `PostMaster` and `SIDManager`, allocates `streamid`, marshals the message, creates `XRootDMsgHandler`, sets behavior flags from `MessageSendParams`, builds or takes ownership of a `HostList`, and sends. On send failure it unmarshals the request, releases the stream ID, deletes the handler, and returns the error.

Redirect flow registers the URL as a virtual redirector, marks the load-balancer host as manager/meta/virtual redirector, enables metalink following, and schedules a redirect through the postmaster. CGI rewriting inspects the protocol request ID, edits the path payload at offset 24 for supported request types, handles `mv` target path specially, and refreshes the transport description.

## State And Persistence

This file mutates transient message buffers, `MessageSendParams`, stream ID allocation state, redirector registry state, and handler-owned host lists. It does not persist to disk. Send failure cleanup is important because stream IDs are persistent within the SID manager until released.

## Dependencies And Integration Points

Dependencies include `DefaultEnv`, `Log`, `SIDManager`, `PostMaster`, `XRootDTransport`, `XRootDMsgHandler`, `RedirectorRegistry`, `URL`, XRootD protocol structures, `XProtocol`, xattr limits, and optional `LocalFileHandler`. It is called by high-level file and filesystem APIs before messages enter the transport layer.

## Risks

Ownership of `sendParams.hostList` is transferred by nulling the pointer; callers must not reuse it. If marshalled state or buffer sizes are wrong, `RewriteCGIAndPath` can corrupt request bodies. `RedirectMessage` deletes `list` after deleting `msgHandler` on failure, so handler ownership must match that cleanup path. `CreateXAttrVec` uses protocol limits but not semantic validation of attribute names. `ProcessSendParams` uses wall-clock `time(0)` and can be affected by time jumps.

## Test Signals

Test signals include successful send path with stream ID allocation/release on failure, checkpoint xeq stream ID rewrite, redirect setup flags, host list ownership transfer, timeout/default expiry behavior, CGI merge for open/stat/mv/locate with replace and append modes, xattr vector limit enforcement, and message description refresh after path rewrite.
