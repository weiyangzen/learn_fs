# sources/user-network-fs/nfs-ganesha/src/include/gsh_types.h

Purpose: This header provides small cross-layer primitive types used throughout Ganesha.

Important APIs/types/functions: `nsecs_elapsed_t` is a 64-bit nanosecond duration type, with `NS_PER_USEC`, `NS_PER_MSEC`, and `NS_PER_SEC` constants. `struct gsh_buffdesc` is a counted buffer descriptor with `addr` and `len`.

Control flow: Buffer descriptors are passed through FSAL handle conversion, hash table keys/values, upcalls, and protocol helpers instead of raw pointer/length pairs. Nanosecond constants support elapsed-time calculations.

State and persistence: The header owns no state. `gsh_buffdesc` often points into caller-owned memory, so ownership and lifetime are external.

Dependencies and integration points: Depends only on standard integer and allocation headers and is included by many core utility and FSAL headers.

Risks: `gsh_buffdesc` does not encode capacity, mutability, or ownership; APIs must document whether `len` is input size or output size. Null `addr` with nonzero length is unsafe unless a callee explicitly permits it.

Test signals: For APIs using `gsh_buffdesc`, test boundary lengths, zero-length buffers, output length updates, and ownership behavior. For elapsed-time users, check unit conversions and overflow assumptions.
