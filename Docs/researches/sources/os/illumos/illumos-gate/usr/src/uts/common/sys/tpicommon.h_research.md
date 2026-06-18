# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tpicommon.h

## Purpose
Common Transport Provider Interface definitions shared by TLI/XTI headers.

## Main Interfaces
- Defines TPI/TLI error constants including `TBADADDR`, `TBADOPT`, `TACCES`, `TBADF`, `TNOADDR`, `TOUTSTATE`, `TBADSEQ`, `TSYSERR`, `TLOOK`, `TBUFOVFLW`, `TFLOW`, `TNOTSUPPORT`, `TPROTO`, and others.
- Defines service types `T_COTS`, `T_COTS_ORD`, `T_CLTS`, and `T_RDMA`.
- Defines option management flags `T_NEGOTIATE`, `T_CHECK`, `T_DEFAULT`, `T_SUCCESS`, `T_FAILURE`, `T_CURRENT`, `T_PARTSUCCESS`, `T_READONLY`, and `T_NOTSUPPORT`.
- Defines boolean and size sentinel constants such as `T_YES`, `T_NO`, `T_INFINITE`, `T_INVALID`, and `T_UNSPEC`.
- Defines `struct opthdr` plus `OPTLEN` and `OPTVAL` helpers for option buffers.

## Dependencies And Relationships
Includes `sys/feature_tests.h`. Included by `tiuser.h` and related transport headers to centralize common constants.

## Research Notes
The file is mostly ABI constants. Additions must avoid colliding with historical XTI/TLI values.
