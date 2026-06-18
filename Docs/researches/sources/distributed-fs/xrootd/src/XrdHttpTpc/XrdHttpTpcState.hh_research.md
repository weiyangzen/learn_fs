# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.hh

Purpose: Declares `TPC::State`, the per-curl-handle state object used for HEAD, push, pull, and multistream range operations.

Important APIs/types/functions: Constructors distinguish default, HEAD-only, and transfer states. Public methods configure transfer range and headers, expose bytes/status/error/content length/digests, reset transient state, duplicate/move state, flush/finalize the stream, and report connection description. Private static callbacks bridge libcurl to member methods.

Control flow: State owns callback data for libcurl but borrows the curl handle. Transfer state attaches read callbacks for push or write callbacks for pull; HEAD state only installs header handling. Multistream uses `Duplicate` and `Move` to clone handles and reset transients between ranges.

State and persistence: Tracks all curl/transfer transients and a non-owning `Stream*`. Header lists are owned by the `State` object. Underlying file data persists through `Stream`.

Dependencies and integration points: Forward-declares CURL and XRootD file/request types; implementation links to libcurl and SFS. Used heavily by `TPCHandler`.

Risks: Borrowed curl and stream pointers require careful lifetime ordering. The default constructor creates an inert state that must be populated by `Move` before use. Copy is disabled but move is manual, not C++ move semantics.

Test signals: Constructor variants, destructor header cleanup, duplicate/move lifecycle in multistream, and behavior when curl handle allocation fails.
