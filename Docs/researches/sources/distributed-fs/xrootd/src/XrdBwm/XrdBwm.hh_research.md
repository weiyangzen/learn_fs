# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwm.hh

Purpose: declares the BWM SFS plugin object model: directory shim, file shim, filesystem singleton, and configuration/runtime fields.

Important APIs/types/functions: `XrdBwmDirectory` derives `XrdSfsDirectory`; `XrdBwmFile` derives `XrdSfsFile` and exposes open/close/fctl/read/write/sync/stat/truncate/CX methods; `XrdBwm` derives `XrdSfsFileSystem`, creates file/directory objects, exposes core SFS operations, `Configure`, config parsing helpers, authorization/policy/logger pointers, and static `dummyHandle`.

Control flow: this header defines the contracts implemented by `XrdBwm.cc` and `XrdBwmConfig.cc`. File objects use `oh` to track the current handle and call into BWM state through the singleton.

State and persistence: fields in `XrdBwm` are long-lived plugin process state. `XrdBwmFile` holds only `tident` and `oh`. No persistent on-disk structures are declared.

Dependencies and integration points: includes `XrdBwmHandle.hh`, XRootD pthread and SFS interfaces; forward-declares authorization, logger, policy, config stream, and version types.

Risks: the header exposes many mutable fields publicly in the “configuration values” block, which couples implementation files to object internals. Destructor intentionally does not clean complex global state. `XrdBwmFile` destructor calls `close` only if `oh` is non-null, including dummy handle behavior.

Test signals: compile ABI against XrdSfs interface, newFile/newDir object creation, destructor cleanup path, and config-driven policy/logger/authorization setup.
