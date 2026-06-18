# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser.h

Public HID parser contract shared by the HID driver and HID STREAMS modules. It defines opaque `hidparser_handle_t`, usage/report description structures, report-id list structures, packet info, parser query functions, HID item tags, usage pages/usages, main-item descriptor bits, and parser status values.

Important query APIs include country code lookup, report packet size lookup, usage attribute lookup, main item data descriptor lookup, ordered usage list extraction, report-id list extraction, and max-packet-size discovery.

The ABI is intentionally descriptor-centric: consumers ask for report IDs, usage metadata, logical ranges, report size/count, and main item attributes rather than walking the raw parser tree. Limits include `USAGE_MAX` of 100 usages per report and `REPORT_ID_MAX` of 10 report IDs per type.

The header codifies common HID pages/usages used by keyboard, mouse, LED, button, generic desktop, and consumer-control modules.
