## sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.cc

Purpose: Implements parsing of SciTags packet-marking experiment/activity codes from CGI query strings.

Important APIs and functions: `XrdNetPMark::getEA(const char *cgi, int &ecode, int &acode)` extracts a combined `scitag.flow` value and splits it into experiment and activity IDs.

Control flow: The method initializes outputs to zero, searches for `scitag.flow=`, parses a decimal integer with `strtol`, accepts only values ending at `&` or end-of-string, checks the total ID range, and if valid shifts/masks into experiment and activity codes. It returns true whenever a syntactically present `scitag.flow` parameter was parsed to an integer terminator, even if out of range, preserving the specification that invalid values mark packets with zero.

State and persistence: Stateless; only caller-provided output references are modified.

Dependencies and integration points: Includes `XrdNetPMark.hh` for ID limits and bit masks. Adjacent PMark config and flow-file code use the parsed codes to begin packet marking handles.

Risks: `strstr` matches `scitag.flow=` anywhere, including inside another parameter name. Negative values and overflow rely on `strtol` behavior and range check. Duplicate parameters use the first occurrence only. The return value distinguishes parameter presence/syntax from absence, not validity of the code.

Test signals: Query strings with no parameter, valid min/max codes, out-of-range values, zero, negative, overflow, non-numeric suffix, duplicate parameters, prefix-name collisions, and parameters followed by `&`.
