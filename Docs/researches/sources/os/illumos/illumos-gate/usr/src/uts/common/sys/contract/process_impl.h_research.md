# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process_impl.h

`process_impl.h` defines private process-contract structures. Templates hold common template data, fatal event mask, parameters, service FMRI/creator strings, service contract id, and creator auxiliary data. Process contracts hold common contract data, member count, inherited contract count, parameter/fatal masks, service metadata, and creator auxiliary data.

It declares the system process template, process contract type, and functions for init, process exit/hardware-error notification, contract transfer, accept/adopt behavior, and `PRCTID` lookup.
