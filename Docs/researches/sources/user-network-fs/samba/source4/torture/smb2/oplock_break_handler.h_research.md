# sources/user-network-fs/samba/source4/torture/smb2/oplock_break_handler.h

## Purpose
This header exposes the shared SMB2 oplock-break testing contract: a common break-tracking struct, handler prototypes, wait helper, and reset helper for torture tests.

## Important APIs, Types, And Functions
`struct break_info` carries the torture context, `oplock_skip_ack`, last SMB2 handle, last break level, SMB2 break request/response object, break count, failure count, failure NTSTATUS, and the transport that received the break. The header declares global `break_info`, `torture_oplock_ack_handler()`, `torture_oplock_ignore_handler()`, and `torture_wait_for_oplock_break()`. The inline `torture_reset_break_info()` zeroes a supplied `struct break_info` and restores its `tctx` pointer.

## Control Flow
Tests include the header, call `torture_reset_break_info(tctx, &break_info)`, install a handler on an SMB2 transport, perform an operation expected to break an oplock, and then call `torture_wait_for_oplock_break()` before checking the global fields.

## State And Persistence
The header itself has no runtime storage except the external declaration, but it defines the layout of the process-global state owned by `oplock_break_handler.c`. Resetting is destructive for all tracked break fields except the torture context pointer restored afterward.

## Dependencies And Integration Points
The declarations require Samba types such as `struct torture_context`, `struct smb2_handle`, `struct smb2_break`, `NTSTATUS`, and `struct smb2_transport` from the including translation unit's Samba headers. It integrates with the SMB2 transport callback signature and the torture framework.

## Risks
Because `break_info` is global, including tests must coordinate resets and cannot safely run independent break assertions on the same process state. The inline reset uses `ZERO_STRUCTP`, so any future fields needing nonzero defaults must be explicitly restored after the zero. Header consumers must include compatible Samba type declarations before or alongside this header.

## Test Signals
Compile-time signals are successful inclusion in SMB2 torture files and type compatibility with the transport oplock callback. Runtime signals are a reset `break_info.count == 0`, `tctx` preserved after reset, and expected handler-populated fields after a break.
