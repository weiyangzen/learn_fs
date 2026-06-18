<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/multipath.conf -->
# sources/test-tools/blktests/tests/srp/multipath.conf

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This source has no `DESCRIPTION` assignment, so its purpose is inferred from its entry points and command surface.

Important APIs/types/functions: .

Control flow: The file contributes data/configuration consumed by the surrounding test harness.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness.

Risks and test signals: primary risk is build or harness drift; signal is make/shell exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/multipath.conf -->
