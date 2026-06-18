# File Research: sources/local-fs/dlm/python/ebpf/dlmhist.py

## Purpose
BCC/eBPF tracing script that measures DLM exclusive noqueue lock latency from kernel `dlm_lock_start` to successful AST completion.

## Behavior
- Attaches tracepoint probes to `dlm:dlm_lock_start`, `dlm:dlm_lock_end`, and `dlm:dlm_ast`.
- Tracks start timestamps in a BPF hash keyed by `ls_id ^ lkb_id`.
- Only records `DLM_LKF_NOQUEUE` and `DLM_LOCK_EX` starts.
- Deletes starts on lock-end errors.
- On AST with successful `sb_status`, records log2 nanosecond latency histogram.
- Waits until Ctrl-C, then prints the histogram.

## Dependencies
- Python BCC package.
- Kernel DLM tracepoints and DLM UAPI headers.

## Risks / Gaps
- Hash key is simple XOR and can collide.
- Script cannot distinguish local-master latency from remote/network latency; comment notes expected two peaks.
