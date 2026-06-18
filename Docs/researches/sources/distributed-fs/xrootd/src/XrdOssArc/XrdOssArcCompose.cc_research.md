# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.cc

Purpose: parses archive/backup logical paths and CGI into dataset/file/archive identifiers, builds archive/member paths, and asks metadata utilities where files live or what their stat metadata is.

Important APIs/types/functions: constructor, `ArcMember`, `ArcPath`, `DSN2Dir`, `Dir2DSN`, `getDSN`, `isArcFile`, `isArcPath`, `isBkpPath`, `isMine`, `SetarName`, static `Stat`, `StatDecode`, and `StatGet`.

Control flow: constructor classifies path as archive or backup by configured prefixes, extracts dataset scope/name, rejects write operations, optionally extracts archive filename from path, otherwise reads `ossarc.fn` from env, parses file scope/name, rejects invalid backup archive filenames, and calls `SetarName()` when a file must be mapped to an archive zip. `SetarName()` runs `BkpUtilProg which` and interprets `!ENOENT`/`!ENOANO`. `Stat()` runs `BkpUtilProg stat cgi`, then decodes CGI fields into a POSIX `stat`.

State and persistence behavior: object state is parsed strings (`dsScope`, `dsName`, `flScope`, `flName`, `arName`) and `didType`. No direct persistence; external utility calls query metadata systems. `DSN2Dir`/`Dir2DSN` encode slashes as `%` for staging directories.

Dependencies: global `Config`, `Elog`, thread-local `ecMsg`, `XrdOucEnv`, `XrdOucProg`, `XrdOucStream`, and `XrdSysE2T`.

Integration points: central parser for `XrdOssArc::Stat`, directory/file wrappers, backup staging, and archive member extraction.

Risks: `minLenFN` is declared but filename validation uses `minLenDSN`; prefix matching accepts configured strings exactly and has a special short archive-prefix case; utility output is single-line/string-protocol based; error details are thread-local; path and CGI ambiguity can select different archive names.

Test signals: archive dataset path, archive member path, backup path requiring `ossarc.fn`, file scope parsing with/without colon, archive suffix rejection for backup, utility `which` success and `!ENOANO`, stat CGI decode, and long path/member buffer errors.
