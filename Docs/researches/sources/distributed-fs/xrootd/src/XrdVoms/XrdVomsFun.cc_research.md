# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.cc

Purpose: Implements the VOMS authorization extraction function that reads proxy certificate chains, extracts VO/group/role/FQAN data via libvoms, populates XrdSecEntity fields, and optionally applies VOMS mapfile name mapping.

Important APIs/types/functions: XrdVomsFun constructor sets default raw cert format. NameOneLine(), FmtExtract(), FmtReplace(), VOMSFun(), and VOMSInit() are key methods. Macros handle SafeFree, debug printing, replacement of <g>/<r>/<vo>/<an>, and space-to-tab conversion.

Control flow: VOMSFun() sets ent.prox to xrdvoms, builds pxy and STACK_OF(X509) from raw XrdCryptoX509Chain, PEM bytes, or Voms_x509_in_t, calls vomsdata::Retrieve(RECURSE_CHAIN), filters VOs/groups, selects first/last/all group tuples, writes ent.vorg/grps/role/endorsements, applies output format replacements, frees temporary chain objects according to input ownership, returns failure if required VOMS fields are absent, and then applies m_mapfile if configured. VOMSInit() parses cfg options by locating tag ranges, validates certfmt and grpopt, builds group/VO hash filters, records format strings/debug level, logs configuration, and configures XrdVomsMapfile.

State/persistence: Per-object configuration includes cert format, group selection mode, debug level, group/VO filters, required string, output formats, logger/error destination, and singleton mapfile pointer. No durable writes.

Dependencies/integration: Uses libvoms, OpenSSL, XrdCryptoX509Chain/X509, XrdSecEntity, XrdOucString/Hash, XrdSysLogger, and XrdVomsMapfile.

Risks: Manual memory ownership around ent fields and X509 stacks is fragile. Config parsing is ad hoc and range-based, so quoted strings and tag ordering deserve tests. Multi-value VO/group/role strings are space-separated and then sometimes tab-normalized, which can affect downstream consumers.

Test signals: Test raw, PEM, and X509 input formats; missing proxy/chain; VOMS retrieval failure; VO/group filters; usefirst/uselast/useall; formatting placeholders; debug output; mapfile success/failure precedence; and sanitizer runs for X509/ent field ownership.
