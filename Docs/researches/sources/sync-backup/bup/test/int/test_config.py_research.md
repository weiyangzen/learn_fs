<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_config.py -->
# sources/sync-backup/bup/test/int/test_config.py

Purpose: tests config URL resolution for remote options. Important APIs are `bup.config`, `bup.url.URL`, `IPv4Address`, and `IPv6Address`. Control flow constructs remote option values and expected URL objects, including local paths, host/path forms, IPv4/IPv6 addresses, and port/user variants, then checks `url_for_remote_opt` behavior. State is in-memory URL/config objects only. Dependencies are Python `ipaddress`, bup URL parsing/rendering, and pytest-style assertions. Risks are ambiguous colon syntax between local paths and host URLs, IPv6 bracket handling, and default scheme/user behavior. Test signals are equality of returned `URL` objects and parsed address fields.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_config.py -->
