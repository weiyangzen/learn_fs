<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.cc

Purpose: Implements message-template parsing and runtime variable substitution for notification, external program, and storage-operation messages.

APIs and control flow: The constructor initializes static variable names such as `$LFN`, `$PFN`, `$USER`, `$HOST`, `$RID`, and `$CGI`. `Parse()` duplicates the message, splits it into literal and variable elements, honors escaped dollars, maps known uppercase variables to enum ids, and rejects templates with more than `maxElem` elements. `Subs()` walks the parsed elements and fills caller-provided data/length arrays. `getVal()` supplies values from `XrdOucMsubsInfo`, converting logical names through `XrdOucName2Name` when PFN/RFN values are needed and caching converted strings in the info object.

State and persistence: Parsed template text is stored in `mText`, with `mData` and `mDlen` recording fragments. Converted PFN/RFN values live in `XrdOucMsubsInfo` buffers until that info object is destroyed.

Dependencies and integration: Depends on `XrdOucEnv`, `XrdOucName2Name`, security/CMS environment keys, and POSIX open flags.

Risks and test signals: Missing values fall back to the literal variable token, which may be intentional but can hide configuration mistakes. Tests should cover escaping, custom env variables, PFN/RFN conversion failures, `$OFLAG` formatting, and the element limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.cc -->
