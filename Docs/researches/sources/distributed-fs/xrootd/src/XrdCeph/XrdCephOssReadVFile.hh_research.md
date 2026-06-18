# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssReadVFile.hh

Purpose: declares the readv decorator used when `ceph.usereadv` is enabled.

Important APIs and types: `XrdCephOssReadVFile : virtual public XrdCephOssFile` overrides `ReadV` and delegates the rest of the file interface. It stores `m_xrdOssDF`, `m_algname`, `std::unique_ptr<IXrdCephReadVAdapter>`, and timing counters for backing Ceph reads.

Control flow and integration: selected by `XrdCephOss::newFile()` before optional buffering. This order means a buffered wrapper delegates `ReadV` to this decorator, while ordinary reads may be buffered outside it.

State and persistence: the decorator owns and deletes the wrapped file. Metrics are process memory only and logged on close.

Dependencies: includes Ceph OSS classes and readv/buffer interfaces, plus `<memory>`.

Risks and test signals: tests should verify algorithm selection, invalid algorithm fallback, destructor ownership, and that decorated write/AIO paths are transparent. Timing counters are atomic but `m_timer_longest` uses load-then-store without compare-exchange, so concurrent reads can under-report longest duration.
