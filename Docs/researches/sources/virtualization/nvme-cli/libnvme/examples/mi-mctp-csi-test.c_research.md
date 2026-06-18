# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-csi-test.c

This C example sends two MI admin commands in parallel over MCTP using different CSI buffers.

Core behavior:
- Supports action `csi-test <controller-id> [<log-id>]`.
- Opens two MCTP endpoints to the same net/eid.
- Sets CSI 0 on one endpoint and CSI 1 on the other.
- Starts a pthread that runs `do_get_log_page()` on the second endpoint.
- Runs `do_get_log_page()` on the first endpoint in the main thread.
- Joins the thread and returns either command’s error.
- `do_get_log_page()` initializes a transport handle for the controller, builds a Get Log command, retrieves a 4096-byte log page, and hexdumps it.

Integration role:
- Tests independent concurrent MCTP endpoint usage and CSI separation.
- Depends on pthreads and MI support.
