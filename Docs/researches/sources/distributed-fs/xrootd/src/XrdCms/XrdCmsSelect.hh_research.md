# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSelect.hh

Purpose: declares selection request/response data structures used by cache, locate, select, and prepare paths to choose CMS nodes.

Important APIs/types: `XrdCmsSelect` carries input path, optional fast RRQ info, avoid mask, selected mask, prepare iovec, options, alternate hash, output vectors, and response data. Option flags encode write/create/truncate/online/defer/peers/refresh/asap/noBind/meta/freshen/replica/retry/multiwrite/advisory/pending/interface and packed/reference/directory/alternate-hash modes. `XrdCmsSelected` describes one candidate node for locate/list output. `XrdCmsSelector` records selection failure reasons and exclusion booleans.

Control flow: selectors fill `Vec`, `smask`, and `Resp` based on options. `XrdCmsSelected` linked lists are returned by cluster list/select operations and formatted for locate responses.

State and persistence: these are transient stack/heap request containers. `XrdCmsSelect::Path` wraps the caller-provided path buffer; no persistent storage.

Dependencies/integration: includes `netinet/in.h` and `XrdCmsKey.hh`; forward declares `XrdCmsRRQInfo`. Used by `XrdCmsNode`, `Cluster`, `Cache`, `RRQ`, and prepare selection code.

Risks: dense bitmask values include overlaps by design (`Create = 0x000A0` combines create/truncate semantics), so consumers must mask correctly. Fixed `SelDSZ=256` response buffer must hold host/error data. Constructor does not initialize every field (`nmask`, `iovP`, `iovN`, vectors, flags), so callers must set required fields before use.

Test signals: option bitmask regression tests, constructor initialization tests, locate formatting length tests, and selection failure reason tests.
