# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pictlist.c

## Summary
`pictlist.c` implements a small private singly linked list mapping Word text/file offsets to picture-data offsets.

## Main Responsibilities
- Stores `picture_block_type` records in insertion order.
- Ignores invalid text offsets and invalid picture-storage offsets.
- Provides cleanup through `vDestroyPictInfoList()`.
- Exposes lookup through `ulGetPictInfoListItem()`.

## Key Dependencies
Uses `antiword.h`, allocation wrappers, `FC_INVALID`, and picture records produced by property parsers such as `prop2.c` and `prop6.c`.

## Filesystem Relevance
No direct filesystem calls. The stored offsets refer to positions inside Word document streams and are later used by image extraction paths.

## Notes
Lookup is linear, which is acceptable for the expected small picture counts in legacy Word documents.
