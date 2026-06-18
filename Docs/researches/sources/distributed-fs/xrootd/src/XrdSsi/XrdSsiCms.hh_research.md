# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.hh

Purpose: declares `XrdSsiCms`, an `XrdSsiCluster` implementation backed by an `XrdCmsClient`. It exposes cluster resource lifecycle and capacity methods to SSI provider code while hiding the CMS client representation.

Important APIs/types: public methods include `Added()`, `Removed()`, `Managers(int &)`, `Resume()`, `Suspend()`, `Resource()`, `Reserve()`, `Release()`, and `Utilization()`. `DataContext()` always returns true, indicating this cluster adapter works in a data-serving context. Constructors support an inert default instance and a CMS-backed instance; the destructor owns `manList`.

Control flow and state: most methods are thin guards around `theCms`; if `theCms` is null they return neutral values or do nothing. `Managers()` returns an internal array of duplicated endpoint strings and sets the count. Private state is `XrdCmsClient *theCms`, `char **manList`, and `int manNum`.

Dependencies and integration: depends on `XrdCms/XrdCmsClient.hh` and the SSI cluster base class. It is a server-side integration point for provider initialization and CMS resource publication. Risks include callers treating `Managers()` output as mutable or longer lived than the object, and neutral returns hiding misconfiguration. Test signals should validate null-object behavior, forwarding semantics, and that the manager count/list remain stable after construction.
