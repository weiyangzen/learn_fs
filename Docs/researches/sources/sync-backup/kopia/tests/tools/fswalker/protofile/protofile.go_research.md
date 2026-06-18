<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/protofile/protofile.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/protofile/protofile.go

This file contains a helper for writing protobuf messages in text format. `WriteTextProto` marshals a `proto.Message` with `prototext.Marshal`, appends a newline if needed, and writes it to a path with mode `0644`.

It is used by the fswalker `walker` and `reporter` wrappers to create temporary policy/config files accepted by the upstream fswalker APIs.

State is only the written temp file. Risks are straightforward: write permissions, non-atomic writes, and caller responsibility for cleanup. Tests for walker/reporter indirectly validate this helper.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/protofile/protofile.go -->
