## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrJob.hh

Purpose: defines the transfer job record passed between `XrdFrmXfrQueue` and `XrdFrmTransfer` workers.

Important APIs/types: `XrdFrmXfrJob` is a plain aggregate with linked-list field `Next`, extra notification destinations `NoteList`, source request file pointer `reqFQ`, request-file key `reqFile`, copied `XrdFrcRequest reqData`, display strings `Type`/`Act`, local `PFN` buffer, `pfnEnd` suffix offset, `RetCode`, and queue number.

State and persistence: the job is runtime state only, but it points back to persistent request files so `Done()` can delete completed requests. The PFN buffer reserves room for sidecar suffixes such as `.fail`, `.anew`, and `.lock`.

Dependencies and integration: used by `XrdFrmXfrQueue` for queue ownership and by `XrdFrmTransfer` for execution. Includes request type and platform path limits.

Risks and test signals: no constructor initializes fields, so queue initialization must set every field before worker use. Tests should validate PFN suffix bounds and cleanup of `NoteList`.
