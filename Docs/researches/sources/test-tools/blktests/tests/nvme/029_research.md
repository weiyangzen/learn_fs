<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/029 -->
# sources/test-tools/blktests/tests/nvme/029

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test userspace IO via nvme-cli read/write interface".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test userspace IO via nvme-cli read/write interface`, `QUICK=1`; functions `requires()` lines 13-17, `set_conditions()` lines 19-21, `test()` lines 55-93; external commands `blockdev`, `dd`, `nvme`, `diff`, `echo`, `cat`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/vm/nr_hugepages`, `/dev/urandom`, `/dev/$`, `/proc/sys/vm/nr_hugepages`, `$FULL`, `$(blockdev --getss "$disk")`, `$((cnt * bs)`, `$(mktemp /tmp/blk_img_XXXXXX)`, `$(cat /proc/sys/vm/nr_hugepages)`, `$(_find_nvme_ns "${def_subsys_uuid}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `blockdev`, `dd`, `nvme`, `diff`, `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/029 -->
