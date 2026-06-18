# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.cc

Purpose: implements the concrete `XrdSsiCms` adapter that lets SSI providers interact with XRootD CMS cluster management while counting SSI resource statistics. The constructor snapshots the manager list from an `XrdCmsClient`, storing each manager as `host:port` strings in a private array that is later exposed through the header API.

Important APIs and control flow: `XrdSsiCms::XrdSsiCms(XrdCmsClient *)` walks `cmsP->Managers()`, counts entries, allocates `manList`, and duplicates formatted manager endpoints. `Added()` and `Removed()` increment `Stats.ResAdds` and `Stats.ResRems` before delegating to `XrdCmsClient::Added()` or `Removed()` if a CMS client exists. The destructor frees every duplicated manager string and deletes the array.

State and persistence: state is process-local only: `theCms`, `manList`, and `manNum`. There is no disk persistence or network I/O in this file beyond delegating to the CMS object. Dependencies include `XrdCmsClient`, `XrdOucTList`, and the global `XrdSsi::Stats`.

Integration points: used wherever SSI needs a cluster object implementing `XrdSsiCluster` for provider initialization and resource advertisements. Risks include trusting the CMS manager list lifetime during construction, fixed 1024-byte formatting buffer for endpoints, and null `theCms` behavior that silently turns methods into no-ops. Test signals should cover empty and multi-manager CMS lists, stats bumps on add/remove, delegation when `theCms` is non-null, and destructor cleanup under sanitizers.
