# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqFAttr.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqFAttr.cc` implements XRootD file-attribute requests for user extended attributes. It decodes wire-format attribute names and values, forces them into the user namespace, dispatches get/set/delete/list operations to the SFS `FAttr` API, and formats per-attribute result vectors. The source was read as a complete 595-line file.

## Important APIs, Types, and Functions

Local `faCTL` owns decoded `XrdSfsFAInfo` entries and tracks parse position. `Decode()` parses name entries encoded as two zero prefix bytes plus a NUL-terminated name, then optional value entries encoded as network-order `kXR_int32` length plus bytes. `FillRC()` writes per-variable mapped return codes into the name prefix area. `IOVec` allocates bounded `iovec` arrays using the platform maximum. `SendErr()` reports decode failures. Protocol methods are `do_FAttr()`, `ProcFAttr()`, `XeqFADel()`, `XeqFAGet()`, `XeqFALsd()`, `XeqFALst()`, and `XeqFASet()`.

## Control Flow

`do_FAttr()` first checks that user xattrs are configured, validates the subcode, determines read/write mode, and chooses handle-targeted or path-targeted processing. Handle mode verifies the file table entry and write mode for modifying requests. Path mode splits path and attribute payload, rejects relative or unsafe paths, normalizes paths, and honors static open-route redirection. `ProcFAttr()` validates the attribute count, initializes `XrdSfsFACtl`, optionally requests access checks, parses names/values unless this is list, and dispatches to delete/get/set/list helpers. Each helper calls `osFS->FAttr()`, maps filesystem errors through `fsError()`, and serializes either per-variable status, values, list buffers, or list-with-data tuples.

## State and Persistence Behavior

The file itself persists no attributes; persistence belongs to the backing filesystem or plugin. Decoding mutates the request buffer in place by replacing the leading two name bytes with `U.` or mapped return-code bytes. `faCTL` owns the `XrdSfsFAInfo` array until ownership is transferred into `XrdSfsFACtl`. Response data often references the mutated request buffer and filesystem-owned buffers for the duration of the response send.

## Dependencies and Integration Points

The handler depends on XProtocol, XrdBuffer, XrdLink, XrdOucErrInfo, `XrdSfsFAttr`, `XrdSfsInterface`, XrdSec credentials, `XrdXrootdFile`, monitor data, `XrdXrootdProtocol`, `XrdXrootdXeq.hh`, and `XrdXrootdXPath.hh`. It integrates with per-link open-file state, path validation from the main executor, static routing, SFS extended-attribute plugins, and XRootD monitor operation codes for read/write-like metadata changes.

## Risks and Edge Cases

Parsing is strict but in-place: malformed lengths, missing NUL terminators, or extra payload bytes return protocol errors, while valid names are rewritten before the SFS call. `SendErr()` reports `ctl.iNum` rather than the last processed index `iEnd`, which may make diagnostics less precise. `XeqFALsd()` has an unreachable fallback return after an earlier return expression; if no non-error entries produce data, the current path returns zero rather than explicitly sending an empty response. `FillRC()` overwrites name prefix bytes with status codes, so any later code expecting the namespace prefix after response construction would be wrong. Attribute count and max name/value sizes are security boundaries.

## Test Signals

Tests should cover unsupported configuration, invalid subcodes, list with nonzero count, get/set/delete with zero or too many variables, handle mode for read-only and write-open files, path mode with CGI and redirects, malformed name prefixes, empty names, overlong names/values, negative value lengths, extra trailing payload, partial per-attribute SFS failures, segmented large get/list responses, `aData` list mode, `isNew` set mode, and user namespace prefix enforcement.
