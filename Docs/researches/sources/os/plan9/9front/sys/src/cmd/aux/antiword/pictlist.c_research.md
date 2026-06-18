# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pictlist.c

Small linked-list registry for Word picture reference offsets.

Key responsibilities:
- Stores `picture_block_type` records in insertion order.
- Skips invalid logical reference offsets and invalid picture-storage offsets.
- Looks up a picture storage file offset by the file offset where the picture marker appears.
- Frees the full picture list and resets anchor/tail state.

Dependencies:
- Uses Antiword allocation helpers and `picture_block_type`/`FC_INVALID`.

Notable risks:
- Lookup is linear.
- State is global and document-scoped; cleanup is required between documents.
