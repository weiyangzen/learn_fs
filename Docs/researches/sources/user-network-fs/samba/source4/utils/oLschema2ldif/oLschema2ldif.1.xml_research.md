<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/oLschema2ldif.1.xml -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/oLschema2ldif.1.xml

## Purpose

This DocBook XML file is the manual page source for `oLschema2ldif(1)`.

## Important APIs, Types, and Functions

- The document defines `refentry`, `refmeta`, `refnamediv`, synopsis, description, options, version, see-also, and author sections.
- It documents `-I input-file` and `-O output-file`.

## Control Flow

There is no executable flow. During the build, Samba's manpage tooling converts this XML into `oLschema2ldif.1`.

## State and Persistence Behavior

It affects installed/generated documentation only.

## Dependencies and Integration Points

The XML uses the DocBook V4.2 DTD and is referenced by `wscript_build` through `manpages='oLschema2ldif.1'`.

## Risks and Edge Cases

The synopsis and options do not document the `-b/--basedn` option that `main.c` requires. The purpose text says "LDAP schema's" and references the historical LDB site, so documentation may be stale relative to the current command behavior.

## Test Signals

Build-time validation of DocBook/manpage generation and user-facing consistency with `oLschema2ldif --help` are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/oLschema2ldif.1.xml -->
