# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tl.h

## Purpose
Transport loopback option and ioctl definitions for peer credential retrieval.

## Main Interfaces
- Defines transport loopback protocol option level `TL_PROT_LEVEL`.
- Defines `TL_OPT_PEER_CRED` and `TL_OPT_PEER_UCRED`.
- Defines `tl_credopt_t`, which carries credential option metadata.
- Defines ioctl base `TL_IOC` and credential option ioctls `TL_IOC_CREDOPT` and `TL_IOC_UCREDOPT`.

## Dependencies And Relationships
Used by local transport/loopback STREAMS modules and consumers needing peer credentials or `ucred` access over local endpoints.

## Research Notes
The file is narrowly focused on local transport credential passing; `TL_OPT_PEER_UCRED` is the richer modern form.
