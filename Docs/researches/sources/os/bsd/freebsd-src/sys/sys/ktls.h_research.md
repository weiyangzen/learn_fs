# File Research: sources/os/bsd/freebsd-src/sys/sys/ktls.h

Defines kernel TLS record structures, socket option ABI structs, exported session state, and kernel session management APIs. User/shared structures describe TLS record headers, TLS 1.2/1.3 AEAD additional data, MAC data, nonce data, enable parameters, get-record header, and exported one-direction session state.

Constants cover TLS versions, record types, maximum message/parameter sizes, GCM/ChaCha/CBC IV sizes, and TX/RX direction ids. `struct tls_enable` carries keys, IV, algorithms, flags, TLS version, and initial record sequence.

Kernel `struct ktls_session` tracks OCF/session offload state, send tag, crypto params, workqueue index, refcount, mode, tasks, socket/inpcb, RX interface/VLAN, pending/reset flags, sequence data, pending records, destroy task, and generation. APIs enable TX/RX, frame/enqueue/free records, query/set modes and sequences, manage offload mismatch/reset, export sessions, copy keys, and refcount/free sessions.
