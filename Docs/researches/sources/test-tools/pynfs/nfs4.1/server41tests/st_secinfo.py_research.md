# sources/test-tools/pynfs/nfs4.1/server41tests/st_secinfo.py

Purpose: tests named `SECINFO` on a created file and confirms `SECINFO` clears current filehandle state such that following `GETFH` returns `NFS4ERR_NOFILEHANDLE`.

Important APIs/types/functions: `testSupported` and `testSupported2`; imports `create_session`, `bad_sessionid`, and `channel_attrs4` are present but not used by active code.

Control flow: each test creates a session and temporary file, records the filehandle/stateid, obtains the parent directory filehandle, issues `SECINFO(name)`, and closes the file. The second test appends `GETFH` after `SECINFO` and expects `NOFILEHANDLE`.

State and persistence behavior: creates a temporary file and open state, then closes it. The key transient protocol state is current filehandle invalidation after `SECINFO`.

Dependencies/integration: uses `use_obj`, `create_file`, `NFS4ops`, and generated constants. It relies on the target server returning legal security flavor information for the created name.

Risks and test signals: no deep validation of returned security flavors is performed; success only means the operation accepted and had the expected filehandle side effect.
