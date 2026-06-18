<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/walker/walker.go

This file wraps fswalker walking. It defines a maximum file size to hash and provides `Walk` plus `WalkPathHash`.

`Walk` writes a temporary policy textproto, creates an upstream walker from the policy file, installs a callback to capture the produced `Walk`, runs the walker, and returns the captured protobuf. `WalkPathHash` builds a policy for a root path that hashes file contents up to the configured max size.

State is temporary policy files and captured walk data. Dependencies are upstream fswalker and `protofile`. Risks include callback not being called, max hash size hiding changes in very large files, cleanup errors ignored, and policy-file API changes. Walker tests cover success and failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker.go -->
