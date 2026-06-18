# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpMkcol.cc

## Purpose
`XrdClHttpOpMkcol.cc` implements `CurlMkcolOp`, the WebDAV directory creation operation used by `Filesystem::MkDir`.

## Important APIs and Functions
`Setup` sets `CURLOPT_CUSTOMREQUEST` to `"MKCOL"`. `Fail` remaps HTTP 405/invalid-request responses to `kXR_ItExists`, matching mkdir-on-existing-directory semantics. `Success` returns OK and optional `MkdirResponseInfo`. `ReleaseHandle` clears the custom request.

## Control Flow
`Filesystem::MkDir` queues this operation. Base `CurlOperation` handles HTTP execution and status conversion; this class only customizes method, success response, and 405 failure mapping.

## State and Persistence
The operation creates a remote collection/directory. In memory it stores only inherited operation state and a response-info flag.

## Dependencies and Integration Points
It depends on response wrappers, XrdCl logging/status constants, and WebDAV server support for MKCOL.

## Risks and Test Signals
Tests should validate 405-to-exists mapping, successful mkdir with/without response info, unsupported WebDAV verb errors, and custom request cleanup for reused handles.
