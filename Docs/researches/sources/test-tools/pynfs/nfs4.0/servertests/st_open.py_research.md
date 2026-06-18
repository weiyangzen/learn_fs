# sources/test-tools/pynfs/nfs4.0/servertests/st_open.py

Purpose: Broad NFSv4 `OPEN` conformance suite covering create modes, normal opens, non-regular-object failures, bad names, invalid/unsupported attributes, `CLAIM_PREVIOUS`, mode/share-deny conflicts, failed-open side effects, open upgrades, replay, and bad open sequence ids.

Important APIs/types/functions: Uses `environment.check/checkdict/get_invalid_utf8strings`, `nfs4lib.get_bitnumattr_dict`, and many client helpers including `create_confirm`, `create_file`, `open_file`, `open_confirm`, `close_file`, `read_file`, `write_file`, and `supportedAttrs`. Test functions run from `testOpen` through `testBadSeqid`.

Control flow: Tests usually initialize a client, build an `OPEN` compound via client wrappers, optionally confirm the open, then verify resulting filehandle/stateid, returned attributes, or expected failure status. Conflict tests use two clients or multiple open owners to trigger share-deny and open-mode behavior.

State and persistence behavior: Creates files under the test home, opens and closes stateids, mutates mode bits, and exercises server sequence/replay caches. Create tests inspect `FATTR4_SIZE`, `FATTR4_MODE`, link support, and returned attrsets.

Dependencies and integration points: Depends on server-test environment, prebuilt test-tree object paths, name/UTF-8 samples, and the pynfs client state machine for open-owner sequence tracking.

Risks: Share-deny and permission checks are sensitive to server policy and AUTH credentials. Replay tests can alter client-side seqid tracking. Some object-type docstrings say `SYMLINK` for block/char/socket/fifo failures, while checks expect protocol-specific statuses.

Test signals: Covers `NFS4_OK`, `NFS4ERR_EXIST`, `NFS4ERR_NOENT`, `NFS4ERR_ISDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_NAMETOOLONG`, `NFS4ERR_NOTDIR`, `NFS4ERR_ATTRNOTSUPP`, `NFS4ERR_RECLAIM_BAD`, `NFS4ERR_NO_GRACE`, `NFS4ERR_ACCESS`, `NFS4ERR_SHARE_DENIED`, `NFS4ERR_OPENMODE`, `NFS4ERR_LOCKED`, and `NFS4ERR_BAD_SEQID`.
