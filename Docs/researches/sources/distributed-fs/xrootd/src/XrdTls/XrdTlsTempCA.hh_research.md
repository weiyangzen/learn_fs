# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.hh

Purpose: Declares XrdTlsTempCA, a manager for consolidated temporary CA and CRL files generated from a CA directory.

Important APIs/types/functions: Public methods are constructor, destructor, IsValid(), CAFilename(), CRLFilename(), and atLeastOneValidCRLFound(). Nested TempCAGuard exposes create(), getCAFD(), getCAFilename(), getCRLFD(), getCRLFilename(), commit(), and RAII cleanup.

Control flow: The class owns a maintenance thread that periodically invokes private Maintenance() and uses pipes for shutdown acknowledgement. Successful refresh interval is 900 seconds; failure retry interval is 10 seconds.

State/persistence: Holds pipe descriptors, XrdSysError reference, CA directory string, shared_ptr file path snapshots, CRL-found boolean, and generated files in an admin temp directory.

Dependencies/integration: Forward declares XrdSysError. Consumers can hand CAFilename()/CRLFilename() to libraries that require file paths instead of OpenSSL stores.

Risks: The class is noncopyable only through TempCAGuard; XrdTlsTempCA itself does not explicitly delete copy/move in the header, though fd/thread ownership makes copying unsafe if attempted. Thread shutdown behavior depends on implementation pipe protocol.

Test signals: Compile for accidental copy prevention expectations, construct/destruct repeatedly under sanitizers, and verify filename snapshots remain valid across refreshes.
