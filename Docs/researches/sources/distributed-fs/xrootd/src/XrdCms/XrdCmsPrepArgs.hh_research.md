# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPrepArgs.hh

Purpose: declares the prepare request job container used to defer or stage CMS prepare operations.

Important APIs/types: public fields mirror parsed request data (`Request`, `Ident`, `reqid`, `notify`, `prty`, `mode`, `path`, `opaque`, `clPath`, `options`, `pathlen`, `ioV`). `DoIt()` delegates selection to `XrdCmsNode::do_SelPrep`. Static `Process()`, `Queue()`, and `getRequest()` manage the global queue. `iovNum` fixes forwarded prepare messages at header plus payload.

Control flow: instances are constructed from `XrdCmsRRData`, queued, then consumed by the static worker. `DoIt()` may delete the object depending on downstream return behavior.

State and persistence: the object owns a single stolen `Data` allocation from `XrdCmsRRData`; pointer fields refer into that buffer. Static queue fields hold pending work process-wide.

Dependencies/integration: includes CMS node/request data, `XrdJob`, and `XrdSysPthread`. It bridges parser/protocol request data to `XrdCmsPrepare` and node selection.

Risks: public mutable fields expose internals to many consumers. Buffer ownership is non-obvious because pointers are aliases into `Data`. Queue state is global, making isolated tests require cleanup or process isolation.

Test signals: construction should leave source `XrdCmsRRData` buffer null; queued objects should be processed FIFO; sanitizer tests should catch use-after-free of aliased fields.
