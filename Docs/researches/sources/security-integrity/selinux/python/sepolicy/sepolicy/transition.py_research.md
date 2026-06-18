# sources/security-integrity/selinux/python/sepolicy/sepolicy/transition.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/transition.py

Purpose: analyzes SELinux process type transitions from a source domain, optionally toward a destination type.

Important APIs and control flow: `_entrypoint(src)` finds allow-rule targets with `entrypoint` permission but is unused in this file. `_get_trans(src)` builds a source list from the type and its attributes, then filters `sepolicy.get_all_transitions()` for process transitions from those sources. `setrans.__init__()` initializes a recursive transition graph. `_process()` stores transitions for each source and, when a destination is requested, recursively follows child transition types until the destination path is found. `out()` formats transition lines with optional conditional text from `sepolicy.get_conditionals()`, using `seen` to avoid cycles. `output()` prints the formatted tree.

State and persistence: in-memory only (`seen`, `sdict`, source/dest fields); reads live policy data.

Dependencies and integration points: imported by `sepolicy transition` CLI and depends on sepolicy transition and conditional APIs.

Risks and test signals: assumes source type info exists and indexes the first matching type record, so missing sources can raise. Recursion is cycle-guarded only during output, while `_process()` uses `sdict` to avoid reprocessing. Tests smoke `sepolicy transition -s httpd_t` and `-s httpd_t -t sendmail_t`.
