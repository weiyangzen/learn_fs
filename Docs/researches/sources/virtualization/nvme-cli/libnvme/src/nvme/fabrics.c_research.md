# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.c

Core NVMe-over-Fabrics implementation for libnvme: context setup, kernel connect/disconnect, discovery log handling, discovery-controller recursion, DIM registration, URI parsing, JSON/config-file discovery, and NBFT boot discovery.

Major responsibilities:
- Defines `/dev/nvme-fabrics` path and writes kernel connect option strings to it.
- Provides string decoders for fabrics enum fields: transport, address family, subtype, TREQ, EFLAGS, SECTYPE, RDMA provider/QP/CMS.
- Creates/frees `libnvmf_context` and installs discovery parser/callback hooks.
- Sets connection, host identity, crypto, device, queue, and reconnect policy fields on the context.
- Builds controller connect option strings from host/controller state and kernel-supported options.
- Connects, initializes, disconnects, and retries controllers.
- Fetches discovery log pages atomically using generation counter validation.
- Parses NVMe-oF boot URIs.
- Performs Discovery Information Management registration for supported discovery controllers.
- Reads NBFT files and connects boot/discovery entries.

Kernel option flow:
- `__nvmf_supported_options()` reads `/dev/nvme-fabrics` to learn supported option names, falling back to a conservative default option set on older `EINVAL` behavior.
- `build_options()` validates transport/address requirements, TLS/concat conflicts, DH-CHAP concat secret requirements, imports TLS keys, and appends supported options.
- `__nvmf_add_ctrl()` opens `/dev/nvme-fabrics`, writes the option string, maps errno values to libnvme connect errors, then parses `instance=<n>` from the kernel response.

Discovery flow:
- `libnvmf_discovery()` locates or creates a discovery controller, optionally reuses a requested device, performs `_nvmf_discovery()`, and disconnects transient controllers.
- `_nvmf_discovery()` fetches discovery logs, invokes hooks, and optionally connects discovered NVMe or discovery subsystems.
- Discovery entries are sanitized by trimming padded fields and fixing FC comma separators.
- TCP discovery entries can set TLS or concat automatically from `treq` and `sectype`.

Registration:
- `libnvmf_is_registration_supported()` checks dctype/cntrltype, falling back to Identify if sysfs fields are unavailable.
- `libnvmf_register_ctrl()` builds and sends a DIM command for TCP discovery controller registration/update/deregistration.

URI and NBFT:
- `libnvmf_uri_parse()` parses `nvme+tcp://...` style URIs into scheme, protocol, userinfo, host, port, path segments, query, and fragment, percent-decoding components.
- NBFT support scans `NBFT*` files, maps HFI MAC/VLAN to Linux interface names, connects SSNS records, and follows discovery descriptors.
- DHCP-related fallbacks retry TCP connects without firmware-provided `host_traddr` when the OS has a different local address.

Dependencies:
- Linux networking headers, sysfs/tree helpers, private fabrics structs, key/TLS helpers from `crypto.c`, NVMe passthrough command builders, and NBFT parser/free helpers.
- Uses cleanup attributes heavily for fd, directory, URI, and heap cleanup.

Risks and notable behaviors:
- Many context setters store borrowed pointers, except TLS `pin:` handling creates an owned exported key string; callers must keep borrowed source strings alive.
- `libnvmf_add_ctrl()` has a likely field typo in its config lookup context: `host_iface` is initialized from `libnvme_ctrl_get_trsvcid(c)`.
- `_nvmf_discovery()` has suspicious child/discover branching: recursive discovery is attempted only under `!child`, which can pass a NULL controller, while successful discovery-controller children are not recursed in that branch.
- URI parsing and unescaping allocate several pieces but does not check every allocation result from `unescape_uri()` or `calloc()` for path segments.
- Option strings are built with repeated `asprintf`, so large untrusted fields are memory-bounded by allocation but still passed to the kernel as-is.
- Tests should cover supported-option parsing, option-string generation, hostname vs literal address behavior, discovery log genctr retry, TLS/concat TREQ decisions, URI parsing, NBFT DHCP fallback, duplicate connect handling, and DIM registration data layout.
