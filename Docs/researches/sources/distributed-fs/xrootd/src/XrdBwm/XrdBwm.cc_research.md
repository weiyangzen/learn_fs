# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.cc

Purpose: implements the BWM SFS filesystem plugin that grants bandwidth/resource “visas” through pseudo-file opens and `fctl(SFS_FCTL_STATV)`.

Important APIs/types/functions: global `BwmEroute`, `BwmTrace`, and singleton `XrdBwmFS`; exported `XrdSfsGetFileSystem`; `XrdBwmDirectory` methods all reject directory operations; `XrdBwmFile::open`, `close`, `fctl`, read/write/stat/sync/truncate methods; `XrdBwm` filesystem operations mostly return unsupported; `Emsg` and `Stall` centralize error/delay responses.

Control flow: plugin construction discovers host/domain and advertise address, creates a dummy handle, and initializes defaults. On plugin load, `Configure` runs. File open requires read/write mode, optional authorization, opaque `bwm.src` and `bwm.dst`, and an LFN embedded after the pseudo prefix. Direction is inferred by matching source/destination host against the local domain, then an `XrdBwmHandle` is allocated. `fctl(SFS_FCTL_STATV)` activates scheduling and returns visa data or async start. `close` retires the handle.

State and persistence: singleton plugin state includes host/domain strings, authorization/policy/logger pointers, locate response, and an open/close mutex. Per-file state is the current `XrdBwmHandle`; no disk namespace is implemented. The policy/logger hold runtime queues and event state.

Dependencies and integration points: integrates with XrdSfs plugin API, XrdAcc authorization, XrdBwmHandle/policy/logger, XrdOucEnv opaque parsing, XrdNet host discovery, and XrdSec identity.

Risks: almost every namespace operation is unsupported, so clients must use the intended pseudo-file/fctl flow. Domain matching with suffix checks can misclassify unusual hostnames. Fixed strings and global singleton design limit reconfiguration. `stat` fabricates block-device-like mode.

Test signals: plugin load/configure, open with missing opaque keys, authorization denial, incoming/outgoing direction inference, `STATV` immediate/queued/failure cases, close cancellation/release, and unsupported method errors.
