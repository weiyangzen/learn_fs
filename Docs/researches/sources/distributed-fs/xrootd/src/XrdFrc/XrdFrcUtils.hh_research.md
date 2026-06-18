<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.hh

## Purpose
`XrdFrcUtils.hh` declares the shared static utility surface implemented in `XrdFrcUtils.cc`. It is the small common API used by FRM admin, configuration, queue, and compatibility code.

## Important APIs
`Ask`, `chkURL`, `makePath`, `makeQDir`, `MapM2O`, `MapR2Q`, `MapV2I`, `Unique`, `updtCpy`, and `Utime` are all static. The header includes `XrdFrcRequest.hh` because mapping APIs expose `XrdFrcRequest::Item` and request option constants.

## Control Flow And State
The class is not meant to hold object state; the constructor and destructor are empty and all useful methods are static. State changes occur in the implementation through filesystem locks, directory creation, xattrs, and timestamps.

## Dependencies And Integration Points
The header depends only on standard time/cstdlib and `XrdFrcRequest`. It forward-declares `XrdFrcXAttrPin`, although this declaration is not used in this header. Consumers include `XrdFrmAdmin`, `XrdFrmConfig`, `XrdFrc` queue code, and compatibility code using lock/pin files.

## Risks And Test Signals
Because this header exposes low-level behavior globally, callers rely on exact return conventions: many functions return `1/0`, while path builders return allocated strings or null. Tests should assert ownership expectations for returned paths, failures from invalid URLs and too-long paths, and that static-only usage does not require object construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.hh -->
