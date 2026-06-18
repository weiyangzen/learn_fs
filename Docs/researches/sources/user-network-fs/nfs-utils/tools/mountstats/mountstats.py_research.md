# sources/user-network-fs/nfs-utils/tools/mountstats/mountstats.py

Purpose: `mountstats.py` parses `/proc/self/mountstats` and displays NFS mount statistics in detailed, raw, nfsstat-like, transport, or iostat-like forms.

Important APIs and control flow: Counter name arrays define NFS events, byte counters, UDP/TCP/RDMA transport counters, and NFSv3/v4 operation names. `DeviceData` parses one mount's NFS and RPC sections, formats reports, computes diffs, accumulates per-version stats, and prints iostat summaries. Top-level commands `mountstats_command`, `nfsstat_command`, and `iostat_command` parse a stats file, filter NFS mountpoints, optionally diff against `--since`, and print selected views. `ICMAction` disambiguates iostat interval/count from mountpoint arguments.

State, dependencies, and integration: State lives in Python dictionaries per mount. The default input is `/proc/self/mountstats`; command-line subcommands use argparse and file handles.

Risks and test signals: Kernel mountstats formats vary; missing fields are padded in some paths but can still raise `KeyError`. `Nfsv4ops` contains duplicate `LAYOUTSTATS`. Integer interval parsing rejects iostat intervals when `--file`/`--since` is used. Tests should use fixture files for v3/v4, TCP/UDP/RDMA, nconnect accumulation, missing counters, diffs after remount, and each subcommand/default dispatch path.
