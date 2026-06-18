# File Research: sources/virtualization/nvme-cli/libnvme/test/uriparser.c

This file is a table-driven unit test for libnvme’s NVMe URI parser.

Core data:
- `struct test_data` stores an input URI plus expected parsed fields: scheme, host, user, protocol, port, path segments, query, and fragment.
- `test_data[]` covers valid URI forms.
- `test_data_bad[]` covers malformed strings expected to fail parsing.

Valid URI coverage includes:
- Basic `nvme://host` with optional trailing slash.
- TCP/RDMA protocol suffixes such as `nvme+tcp://...` and `nvme+rdma://...`.
- IPv4 and bracketed IPv6 hosts.
- Ports and absent ports.
- Path normalization with repeated slashes and trailing slashes.
- Query and fragment parsing, including ordering where `#fragment?query` treats `?query` as fragment content.
- Userinfo, including password-like `user:pass` and user strings containing bracketed IPv6-looking text.
- Percent-decoding in host, user, path, query, and fragment.

Test flow:
- `test_uriparser()` loops valid cases, calls `libnvmf_uri_parse()`, asserts every getter result, checks NULL path termination, frees via `libnvmf_uri_free()`, and prints OK.
- `test_uriparser_bad()` verifies malformed strings return failure and leave `parsed_data == NULL`.

Integration:
- Uses `<ccan/array_size/array_size.h>` for static table sizing.
- Uses public parser APIs: `libnvmf_uri_parse()`, `libnvmf_uri_get_scheme()`, `libnvmf_uri_get_protocol()`, `libnvmf_uri_get_host()`, `libnvmf_uri_get_port()`, `libnvmf_uri_get_path_segments()`, `libnvmf_uri_get_query()`, `libnvmf_uri_get_fragment()`, and `libnvmf_uri_free()`.
- Meson builds it only when fabrics support is enabled.

Risk and maintenance notes:
- The test relies on `assert()`, so compiling with `NDEBUG` would neuter validation.
- The fixed `path[7]` expectation array is sufficient for current cases but should be enlarged if deeper paths are added.
