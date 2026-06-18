# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hid_parser_driver.h

Private HID parser interface for the HID driver. It exposes parser lifecycle and driver-only query functions, not general HID STREAMS module APIs.

Exports `hidparser_parse_report_descriptor()`, `hidparser_free_report_descriptor_handle()`, `hidparser_get_top_level_collection_usage()`, and `hidparser_lookup_usage_collection()`. These let the HID driver parse a raw HID report descriptor, free the opaque handle, determine top-level collection usage for module selection, and test for a usage collection.

The API depends on `usb_hid_descr_t` and `hidparser_handle_t` defined elsewhere. Return comments use parser success/failure status names and make clear that parse failure is expected to be reported through `HID_PARSER_ERROR`-style values.
