# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs.h

Public control-code header for the contract filesystem mounted at `/system/contract`. It defines ioctl/message command values for template, control, status, and event endpoints.

Key elements:
- Defines `CTFS_ROOT` as `/system/contract`.
- Defines the `CTFS_PREFIX` and `CTFS_IOC(x, y)` encoding used for command values.
- Template-file commands activate, clear, create from, set, and get contract templates.
- Control-file commands abandon, acknowledge, request more negotiation quantum, adopt, create a new contract, and negative-acknowledge negotiation.
- Status-file command obtains contract status.
- Event-endpoint commands reset queue position, receive normal or critical events, skip current event, and request reliable receipt.

Dependencies:
- Includes `sys/contract.h` for contract subsystem types and constants used by CTFS clients.
- Consumed by contract filesystem vnode operations and user/kernel CTFS clients.

Research notes:
- This header is command-number only; CTFS object layouts and vnode state live in `ctfs_impl.h`.
- Commands are grouped by virtual file role, reflecting CTFS's file-oriented control model.
