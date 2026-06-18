# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/41

Purpose: Linux reporter parse fixture for syzkaller. It expects `UBSAN: undefined-behaviour in ip_idents_reserve`, type `UBSAN`, corrupted `N`, panicked `N`. The log covers an arithmetic overflow detected by UBSAN in the IPv4 IP ID reservation path.

Important APIs, types, and functions: this static fixture targets UBSAN report recognition in the Linux reporter. Relevant frames include `dump_stack`, `ubsan_epilogue`, `handle_overflow`, `__ubsan_handle_add_overflow`, `ip_idents_reserve`, and `__ip_select_ident`.

Control flow: the harness parses the fixture headers and 18 log lines, then expects the UBSAN title extractor to skip generic UBSAN helpers and select `ip_idents_reserve`. No panic path is present.

State and persistence behavior: state is confined to fixture text and transient parse results. The parser must preserve the non-panicked result and keep the report non-corrupted.

Dependencies, integration points, risks, and test signals: this protects syzkaller grouping for UBSAN undefined behavior in networking code. Risks include collapsing all overflow reports into `__ubsan_handle_add_overflow` or requiring a panic. Success is title equality, `UBSAN` type, and no panic flag.
