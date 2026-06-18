# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_ktls.c

## Summary
Implements FreeBSD kernel TLS (KTLS) session setup, software crypto scheduling, ifnet/TOE offload selection, RX record assembly/decryption, TX framing/encryption, offload reset, and KTLS statistics/sysctls.

## Main Responsibilities
- Validates and deep-copies userspace `tls_enable` parameters.
- Creates, clones, references, destroys, and exports KTLS sessions.
- Starts per-CPU KTLS worker threads and optional per-domain reclaim threads.
- Selects TOE, ifnet, or software TLS for TX/RX.
- Frames outbound TLS records into `M_EXTPG` mbufs.
- Queues software encryption work and marks records ready when crypto completes.
- Converts inbound encrypted byte streams into decrypted TLS record control messages.
- Handles route/interface changes by resetting send/receive TLS tags.
- Disables ifnet TLS when retransmission behavior makes inline offload inefficient.

## Key APIs
- Setup/cleanup: `ktls_copyin_tls_enable()`, `ktls_cleanup_tls_enable()`, `ktls_enable_rx()`, `ktls_enable_tx()`.
- Mode/query/control: `ktls_get_rx_mode()`, `ktls_get_tx_mode()`, `ktls_set_tx_mode()`, `ktls_get_rx_sequence()`.
- RX path: `ktls_pending_rx_info()`, `ktls_check_rx()`, `ktls_input_ifp_mismatch()`.
- TX path: `ktls_seq()`, `ktls_frame()`, `ktls_enqueue()`, `ktls_enqueue_to_free()`, `ktls_output_eagain()`.
- Lifetime/export: `ktls_destroy()`, `ktls_disable_ifnet()`, `ktls_session_to_xktls_onedir()`, `ktls_session_copy_keys()`.

## Important Behavior
Supported protocol versions are TLS 1.0 through TLS 1.3. Supported ciphers are AES-GCM, AES-CBC, and ChaCha20-Poly1305 with version-specific IV, auth-key, and trailer rules. AES-CBC can be disabled by `kern.ipc.tls.cbc_enable`.

KTLS initialization is lazy. The first session creation starts per-CPU worker queues and, when the software buffer cache is enabled, reclaim threads that try to recover contiguous `ktls_maxlen` buffers per NUMA domain.

TX setup requires TCP and, for TX, unmapped external-page mbufs. The selection order is TOE, ifnet TLS, then software TLS. RX first creates an OCF-capable software session, marks existing receive-buffer bytes as not-ready TLS data, then prefers TOE, ifnet RX TLS, or software mode.

`ktls_frame()` adds TLS headers/trailers to each outbound `M_EXTPG` record, assigns the session pointer, emits TLS 1.2 GCM explicit nonces and TLS 1.1+ CBC IVs, encodes TLS 1.3 as application-data records, and marks software records `M_NOTREADY`.

Software TX encryption is queued by workqueue index selected from RSS or flowid/NUMA information. TLS 1.0 CBC sessions require sequential encryption, so out-of-order sendfile completions are held in `pending_records` until their sequence number is next.

RX uses `sb_mtls` as a chain of not-ready encrypted bytes. Once a full TLS record is present, a worker detaches that record, decrypts or recrypts as needed, trims header/trailer, creates a `TLS_GET_RECORD` control mbuf, and appends the decrypted payload as a socket-buffer record.

If a NIC-decrypted RX stream falls out of sync or software had to decrypt a record, `ktls_resync_ifnet()` updates the hardware receive tag with the next TLS header sequence. Route or interface changes schedule reset tasks for send/receive tags.

## State and Synchronization
Session lifetime uses refcounts and UMA allocation. TX sessions hold an inpcb reference. Work queues are protected by per-queue mutexes and processed by bound kernel threads. Socket buffer transitions use socket I/O locks and sockbuf locks; inpcb write locks protect TX mode changes and send-tag pointers read by output paths.

## Risks
Lifetime and lock ordering are complex: sessions can be referenced by sockets, mbufs, taskqueue jobs, OCF callbacks, send tags, and pending TLS 1.0 queues. Error paths can drop TCP connections for failed TX tag reset or crypto failures. RX accepts direct mbuf-chain manipulation and must maintain socket buffer accounting precisely across encrypted, decrypted, detached, and discarded records.
