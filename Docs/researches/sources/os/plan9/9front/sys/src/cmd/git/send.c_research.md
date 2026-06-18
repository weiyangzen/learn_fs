# File Research: sources/os/plan9/9front/sys/src/cmd/git/send.c

Implements client-side receive-pack push. It builds requested local updates from selected branches, all refs, and deletions, reads remote advertised refs/capabilities, checks whether non-forced updates are fast-forwards using `ancestor`, sends update pkt-lines, writes a pack of local objects absent from the remote, and optionally reads report-status.

It prints machine-readable status lines consumed by `git/push`: `uptodate`, `update`, and delete/update failures via exit status. It handles branch ref normalization and remote deletion by setting the desired hash to `Zhash`.
