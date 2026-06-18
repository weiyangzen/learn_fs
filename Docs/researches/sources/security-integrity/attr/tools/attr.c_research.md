## sources/security-integrity/attr/tools/attr.c

Purpose: legacy IRIX-style CLI for get/set/remove/list extended attributes.

`main` parses one of `-s/-g/-r/-l`, namespace flags `-R/-S`, follow flag `-L`, quiet mode, and optional `-V` value. It calls deprecated `attr_set`, `attr_get`, `attr_remove`, and cursor-based `attr_list`, reading set values from stdin when omitted and writing get values to stdout. State is process-local buffers and attrlist cursor. Dependencies are `attr/attributes.h`, gettext, and libmisc i18n. Risks include fixed max value size, deprecated API warnings suppressed, only one pathname allowed, root/security namespace privilege requirements, and verbose mode mixing binary values with text. Tests should cover all operations, stdin values, namespace flags, and quiet listing.
