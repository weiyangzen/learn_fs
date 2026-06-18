# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser_impl.h

Implementation-private HID parser model. It defines linked-list entities for parser attributes and main items, the internal `hidparser_handle` containing the parse tree and HID descriptor pointer, scanner token state, attribute stacks for PUSH/POP handling, and additional parser tag/error constants.

The parser tree is built from `entity_item_t` nodes representing collection/input/output/feature/end-collection items. Each node can carry inherited attributes, child/data pointers, sibling links, and collection ancestry.

The scanner/token bridge `hidparser_tok_t` tracks token bytes, raw descriptor buffer, current descriptor index/token, current global/local item lists, and the global-item stack.

Constants include unexposed local/global items such as set delimiter, usage page, push/pop, end collection, raw item tags, error masks, extended-item marker, and token text buffer length.
