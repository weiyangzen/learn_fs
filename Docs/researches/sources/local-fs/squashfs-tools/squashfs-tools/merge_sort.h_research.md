# File Research: sources/local-fs/squashfs-tools/squashfs-tools/merge_sort.h

Macro header implementing `SORT(FUNCTION_NAME, LIST_TYPE, NAME, NEXT)`, a bottom-up in-place linked-list merge sort generator. It sorts by `strcmp(l1->NAME, l2->NAME)` and rewires `NEXT` pointers without extra node storage.

The macro assumes a counted singly linked list, string sort key field, and mutable head pointer. It is stable for equal names because `<= 0` takes from the left list first.

Primary risk is macro fragility: it depends on including code having `strcmp()` visible and provides no type checking beyond generated C.
