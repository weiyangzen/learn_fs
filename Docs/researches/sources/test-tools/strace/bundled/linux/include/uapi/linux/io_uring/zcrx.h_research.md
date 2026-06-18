# sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/zcrx.h

Purpose: declares the io_uring zero-copy receive ABI for registering receive queues, memory areas, refill queue offsets, and auxiliary control operations.

Important APIs/types/functions: important layouts include `io_uring_zcrx_rqe`, `io_uring_zcrx_cqe`, `io_uring_zcrx_offsets`, `io_uring_zcrx_area_reg`, `io_uring_zcrx_ifq_reg`, and `zcrx_ctrl`. Flags include `IORING_ZCRX_AREA_DMABUF`, `ZCRX_REG_IMPORT`, `ZCRX_REG_NODEV`, and `ZCRX_FEATURE_RX_PAGE_SIZE`.

Control flow: user space registers an interface queue with `IORING_REGISTER_ZCRX_IFQ`, supplies or imports backing area metadata, obtains ring offsets and a `zcrx_id`, refills buffers through RQEs, and uses `IORING_REGISTER_ZCRX_CTRL` for flush or export operations.

State/persistence behavior: registration creates persistent zcrx state tied to the ring and possibly a netdev RX queue or dmabuf. Export can create a separate fd; flush affects queued refill state.

Dependencies/integration: depends on Linux integer types and is included by `io_uring.h`. It also integrates with netdev queue/page-pool concepts via queue indexes and dmabuf registration.

Risks and test signals: ABI is new and pointer-heavy; offsets encode area IDs in high bits. Tests should cover area mask formatting, nodev/import flags, dmabuf fd handling, exported fd output, and reserved-field validation.
