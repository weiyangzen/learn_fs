# sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo_no_name.py

Purpose: tests `SECINFO_NO_NAME` styles on root and home filehandles, including current-filehandle clearing behavior.

Important APIs/types/functions: `testSupported`, `testSupported2`, `testSupported3`, and `testSupported4`.

Control flow: tests create a client/session, run `PUTROOTFH` or `env.home`, then call `SECINFO_NO_NAME` with style `0` or `SECINFO_STYLE4_PARENT`. One test appends `GETFH` and expects `NOFILEHANDLE`; root-parent style expects `NFS4ERR_NOENT`; home-parent style expects success.

State and persistence behavior: no durable objects are created. The state under test is the current filehandle before and after `SECINFO_NO_NAME`.

Dependencies/integration: uses `NFS4ops`, environment home ops, and NFSv4.1 security-info constants.

Risks and test signals: the module prints the compound result in `testSupported2`, which is useful for debugging but noisy. It validates statuses only, not returned flavor contents.
