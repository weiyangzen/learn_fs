<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/032 -->
# sources/test-tools/blktests/tests/nvme/032

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme pci adapter rescan/reset/remove during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `nvme_trtype=pci`, `DESCRIPTION=test nvme pci adapter rescan/reset/remove during I/O`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 21-24, `device_requires()` lines 26-28, `test_device()` lines 30-74; external commands `nvme`, `echo`, `sleep`.

Control flow: `requires()` uses gates `_have_fio`. `device_requires()` uses gates `_require_test_dev_is_nvme_pci`. `test_device()` uses commands `echo`, `sleep`, `nvme`.

State and persistence behavior: touches state paths such as `/sys/bus/pci/devices/${pdev}`, `/sys/bus/pci/rescan`, `/dev/null`, `$(_get_pci_dev_from_blkdev)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_require_test_dev_is_nvme_pci`; runtime command surface includes `nvme`, `echo`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/032 -->
