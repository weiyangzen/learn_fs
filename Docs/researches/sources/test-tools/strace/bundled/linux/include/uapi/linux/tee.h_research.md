# sources/test-tools/strace/bundled/linux/include/uapi/linux/tee.h

## Purpose

Defines the Trusted Execution Environment character-device ioctl ABI used by OP-TEE, AMDTEE, TSTEE, QTEE, and supplicant interfaces. strace uses it to decode `/dev/tee*` and `/dev/teepriv*` ioctls, shared memory operations, session management, invocation parameters, and object invocation.

## Important APIs, Types, and Dependencies

The header depends on `linux/ioctl.h` and `linux/types.h`. It exports `TEE_IOC_MAGIC`, max argument size, generic capability bits, implementation ids, OP-TEE capabilities, `struct tee_ioctl_version_data`, shared-memory allocation/register structs, `tee_ioctl_buf_data`, parameter attribute types for values, memrefs, user buffers, and object refs, login constants, `struct tee_ioctl_param`, UUID length, session open/invoke/cancel/close structs, supplicant receive/send structs, shared-memory fd registration, and `struct tee_ioctl_object_invoke_arg`. Ioctls include `TEE_IOC_VERSION`, `SHM_ALLOC`, `OPEN_SESSION`, `INVOKE`, `CANCEL`, `CLOSE_SESSION`, `SUPPL_RECV`, `SUPPL_SEND`, `SHM_REGISTER_FD`, `SHM_REGISTER`, and `OBJECT_INVOKE`.

## Control Flow, State, and Integration

Runtime flow is ioctl based: query driver version, allocate or register shared memory, open a trusted application session with typed parameters, invoke commands, cancel or close sessions, and exchange supplicant RPC messages. Persistent state is file-descriptor scoped shared memory handles, open sessions, supplicant queues, and TEE-side object references.

## Risks and Test Signals

Risks include decoding variably sized parameter arrays from `tee_ioctl_buf_data`, leaking sensitive buffer/key material in traces, confusing memory reference kinds, and alignment of 64-bit user pointers. Test signals include ioctl name coverage, parameter attribute decoding, login method names, shared-memory fd handling, and object-ref invocation formatting.
