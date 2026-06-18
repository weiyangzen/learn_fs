<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/058 -->
# sources/test-tools/blktests/tests/nvme/058

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test rapid namespace remapping".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test rapid namespace remapping`; functions `requires()` lines 11-15, `set_conditions()` lines 17-19, `_setup_ana()` lines 21-52, `test()` lines 54-112; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `_setup_ana`; commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(( portno + 1 )`, `$(losetup -f --show "${file_path}")`, `$(uuidgen)`, `$(( (i % 3)`, `$(seq 1 "${num_namespaces}" | shuf)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/058 -->
