# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.cc

Purpose: coordinates concurrent manager connection attempts so a server forms a minimal manager tree: either connections to all root nodes or one interior supervisor, avoiding phantom arcs.

Important APIs/types/functions: constructor, `Abort()`, `Connect()`, `Disc()`, `Register()`, and `Trying()`, plus private semaphore helpers `Pause()` and `Redrive()` from the header.

Control flow: `Register()` assigns each manager connection worker a table slot. `Trying()` records the level being attempted and enforces rules: aborted workers stop; if already connected to an interior node, later workers wait; root-level attempts wake waiting workers and force them back to root discovery; only one non-root attempt may proceed at a time. `Connect()` accepts a root connection only when all max connections are root, but an interior connection disbands other connected root nodes by sending `kYR_disc` and marks the tree connected to that supervisor. `Disc()` marks a lost connection active again and reopens connection attempts if the root set or selected interior connection was lost. `Abort()` wakes all waiters with level zero and permanently marks the tree aborted.

State and persistence behavior: all state is in-memory connection coordination: per-slot status, level, node pointer, counts of connected/waiting workers, selected connection level/id, root flag, and overall status.

Dependencies: `XrdCmsManager::MTMax`, `XrdCmsNode::Send()`, `YProtocol.hh` for `kYR_disc`, mutex/semaphore primitives, and CMS logging/tracing.

Integration points: `XrdCmsManager::Run()` creates a fresh tree per manager-site run. Connection workers consult it during topology discovery and manager redirects/reconfiguration abort it.

Risks: semaphore wakeups and status transitions are delicate; missing `Redrive()` can strand workers. `Register()` assumes at most `MTMax` callers and performs no bounds check. `Connect()` sends disconnects while holding the tree mutex, so blocking send behavior would be dangerous if `Send()` can stall. Aborted state is terminal.

Test signals: simulated parallel root/interior attempts, wake/retry behavior, disconnect of selected supervisor, abort with waiters, max-slot bounds under stress, and topology invariants after non-deterministic connection order.
