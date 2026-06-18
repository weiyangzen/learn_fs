<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplay.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplay.cc

Purpose: implements `xrdreplay`, a tool that reads recorder CSV output, optionally rewrites arguments, replays or simulates the captured XrdCl operations with original timing, and reports per-file and aggregate IO metrics. It can also create or verify input datasets implied by read samples.

Important APIs/types/functions: `BufferPool` limits replay buffer memory via `XRD_MAXBUFFERSIZE`; `mytimer_t` measures elapsed time; `barrier_t` posts semaphores when async operations complete; `AssureFile()` verifies or creates files for read datasets; `ActionExecutor` parses action arguments and submits XrdCl file operations; `ToColumns()` parses quoted CSV rows; `ParseInput()` groups rows by original file id into per-file action timelines; `ExecuteActions()` runs one file timeline in a thread; `main()` coordinates parse, replay, reporting, dataset create/verify, and exit status.

Control flow: input rows are parsed into columns, optional regex replacements are applied to the argument field, file ids are mapped to new `XrdCl::File(false)` instances, unsuccessful recorded rows are counted, and successful rows become `ActionExecutor` entries ordered by start time. Unless print/simulate mode is active, per-file threads sleep until each recorded relative start time adjusted by `--speed`, submit async operations, and use semaphores to avoid exiting before final callbacks. Main joins all threads and prints long, summary, json, or dataset assurance output.

State/persistence: replay itself persists no normal output files except when `--create` or `--truncate` creates remote/local files via XrdCl operations. In-memory state includes per-file action lists, metrics, response error counts, buffers, and file objects.

Dependencies/integration: integrates with XrdCl high-level operation wrappers (`Open`, `Read`, `Write`, `VectorRead`, etc.), `XrdCl::File`, `XrdCl::Utils::splitString`, `XrdSysSemaphore`, `ActionMetrics`, and `ReplayArgs`.

Risks/test signals: the CSV parser is custom and does not implement general CSV escaping. Regex replacement validates token count after indexing `tokens[0]`, so malformed replacement strings are risky. `GetVectorReadArgs()` reserves `tokens.size()-1`, which underflows for empty args. JSON summary has metric copy/paste errors (`PgRead::n` used for pgwrite and `VectorRead::n` for vectorwrite) and a misspelled `bandwdith` key. Non-json write bandwidth prints read bytes. Tests should cover CSV rows with quoted fields, unsuccessful sample suppression, print versus replay timing, speed scaling, memory cap blocking/reclaim, vector operations, dataset creation/verification, json summary values, and callback status mismatch accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplay.cc -->
