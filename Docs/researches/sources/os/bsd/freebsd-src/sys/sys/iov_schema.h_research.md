# File Research: sources/os/bsd/freebsd-src/sys/sys/iov_schema.h

Kernel helper API for constructing SR-IOV configuration schema nvlists. Flags identify parameters with defaults and required parameters.

Exports allocation of schema nodes and typed parameter adders for bool, string, uint8/16/32/64, unicast MAC, and VLAN values. This complements `iov.h`: PF drivers use these helpers to describe configuration accepted by `IOV_CONFIG`.
