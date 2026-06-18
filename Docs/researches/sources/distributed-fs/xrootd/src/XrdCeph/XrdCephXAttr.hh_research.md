# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.hh

Purpose: declares `XrdCephXAttr`, the Ceph-backed implementation of XRootD's extended attribute interface.

Important APIs: overrides `Del`, `Free`, `Get`, `List`, and `Set` from `XrdSysXAttr`. Comments document path/default precedence and return conventions for each xattr operation.

Control flow and integration: the class is instantiated by the `XrdSysGetXAttrObject` plugin entry point in the implementation file. It delegates all real work to the POSIX facade.

State and persistence: no member state; xattrs are persistent Ceph object metadata.

Dependencies: includes `XrdSys/XrdSysXAttr.hh`.

Risks and test signals: tests should validate behavior with open fds versus paths, absent attributes, binary values, and list memory ownership. The same default-parameter conflict noted in comments applies when OSS and xattr plugins are both configured.
