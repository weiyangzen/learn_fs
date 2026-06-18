# File Research: sources/virtualization/nvme-cli/Documentation/asciidoc.conf

- Purpose: AsciiDoc configuration for nvme-cli documentation.
- Key behavior: defines the `linknvme:command[section]` macro for DocBook and XHTML output.
- Manpage integration: custom DocBook header emits `NVMe` source, `{nvme_version}`, and `NVMe Manual` metadata.
- Compatibility: includes workarounds for older docbook-xsl/listing and verse block handling.
