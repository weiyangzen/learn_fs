# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.8.in

## Purpose
Manual page template for `o2cluster(8)`.

## Main Content
- Describes `o2cluster` as a utility for changing or listing the cluster stack stamped on an OCFS2 filesystem.
- Documents:
  - `--show-ondisk`
  - `--show-running`
  - `--update[=<clusterstack>]`
  - `--verbose`
  - `--version`
  - `--yes`
  - `--no`
- Explains cluster stack formats:
  - `default`
  - `<stack>,<cluster>,<hbmode>`, e.g. `o2cb,mycluster,global`
- Lists valid stacks: `o2cb`, `pcmk`, `cman`.
- Explains heartbeat modes: `local`, `global`, and `none`.
- Warns that clean journals are used as a safety signal, but there remains a race before updating the on-disk cluster stack.
- Advises running `fsck.ocfs2` after dirty journal scenarios.

## Notes
The section header `.SH "SPECIFYING CLUSTER STACK` is missing a closing quote in the template.
