<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.cpp -->
# sources/user-network-fs/s3fs-fuse/src/addhead.cpp

Purpose: Implements `AdditionalHeader`, a singleton that loads file-extension or regex based rules and injects additional HTTP headers into S3 request metadata or curl header lists.

Important APIs, types, and functions: Implements destructor, `Load`, `Unload`, `AddHeader(headers_t&, const char*)`, `AddHeader(curl_slist*, const char*)`, and `Dump`. Uses `ADD_HEAD_REGEX` prefix `reg:` for regex rules and `curl_slist_sort_insert` to build sorted curl headers.

Control flow: `Load` clears existing rules, opens the configured file, skips blank/comment lines, parses optional key/suffix, header name, and remainder-of-line value. Keys beginning with `reg:` are compiled as POSIX extended regex with `REG_NOSUB`; other keys are treated as suffix strings. Valid rules are appended to `addheadlist` and enable the singleton. `AddHeader` scans every rule for a given path, matches regex or suffix, and writes matching headers into `headers_t`; the curl overload converts those pairs into a curl slist. `Dump` logs the loaded rules only when debug logging is enabled.

State and persistence: In-memory singleton state consists of `is_enable` and `addheadlist`. The input configuration file is persistent external state, but not modified here.

Dependencies and integration points: Depends on `addhead.h`, `metaheader.h` `headers_t`, POSIX regex, `curl_util.h`, and `s3fs_logger.h`. The manpage's `ahbe_conf` option documents the configuration consumed here.

Risks: Suffix matching requires `basestring.length() < pathlength`, so a suffix equal to the entire path does not match. Duplicate matching header keys collapse in `headers_t`, so later matches overwrite earlier values even though the scan allows duplicate rules. Regex compile errors log and skip the rule, while some parse errors unload all rules and fail. Values preserve the remainder after the header token, so spacing matters.

Test signals: Unit tests should cover comments/blank lines, empty suffix as match-all, suffix matches and non-matches including equal-length path, regex matches and invalid regex, duplicate header precedence, curl slist output ordering, null file/path handling, and unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.cpp -->
