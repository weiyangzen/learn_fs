# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.hh

Purpose: declares `XrdOssArcCompose`, the data-id parser and path composer for archive and backup namespaces.

Important APIs/types/functions: public string fields for dataset/file/archive names, enum `pType {isARC,isBKP}`, `ArcMember`, `ArcPath`, static directory encoders, path classifiers, static `Stat`, and constructor with `isW`/`optfn` controls.

Control flow: the constructor returns status through an `int&` instead of throwing. Callers inspect `EDOM` to pass non-archive paths through and other errors to fail archive handling.

State and persistence behavior: transient parse result only. It does not own external resources and has a trivial destructor.

Dependencies: `<cstring>`, `<string>`, forward declarations for `stat` and `XrdOucEnv`.

Integration points: used by nearly every archive wrapper to determine whether a path belongs to this plug-in and how to address archive files and members.

Risks: public mutable fields make invariants easy to break after construction; static minimum lengths are private but not configurable here; return-by-reference status requires disciplined callers.

Test signals: construction return codes, public field population, static classifier consistency with configured prefixes, path/member composition, and non-archive `EDOM` pass-through.
