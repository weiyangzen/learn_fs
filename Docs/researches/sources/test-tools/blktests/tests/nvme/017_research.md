<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/017 -->
# sources/test-tools/blktests/tests/nvme/017

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create/delete many file-ns and test discovery".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create/delete many file-ns and test discovery`; functions `requires()` lines 11-14, `set_conditions()` lines 16-18, `test()` lines 20-55; external commands `echo`.

Control flow: `requires()` uses gates `_require_nvme_trtype_is_loop`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(_nvme_def_file_path)`, `$((def_nsid + i - 1)`, `$(_create_nvmet_port)`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_nvme_trtype_is_loop`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/017 -->
