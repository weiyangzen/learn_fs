# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Weka

Purpose: Python advisory helper to prefetch or release Weka tiered-storage data referenced by an archive manifest. Commands are `prepare <scope> <manifest>` and `dispose <scope> <manifest>`.

Important APIs/functions: `get_Manifest()` reads the first line of the manifest and parses it with `ast.literal_eval`; the expected rows include PFNs at index 1. `Wekafy(action, argv)` extracts PFNs, batches them in groups of 100, and runs either `weka fs tier fetch` or `weka fs tier release`. `Main()` dispatches `prepare` and `dispose`. Debug mode appends `-v` to Weka commands.

State/persistence: no metadata persistence, but it can change Weka tier residency. The script deliberately exits 0 from `Emsg()` even on failures because it treats Weka actions as advisory resource hints rather than correctness gates.

Dependencies/integration: depends on `weka` CLI and manifest format created by backup setup. The source uses `subprocess.run` inside `Execute()` but does not import `subprocess`, so any execution path would raise `NameError`; `get_Manifest()` references `manFN` instead of `ManFN` in one error path. Tests should cover missing import, manifest parsing, batching, advisory success semantics, and CLI argument validation.
