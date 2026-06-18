# sources/sync-backup/bup/test/int/test_url.py

Purpose: tests byte URL parsing/rendering, dot-encoded relative paths, percent escaping, host/user/port handling, IPv4/IPv6 representation, and authentication requirements.

Important APIs/types/functions: `bup.url.URL`, `render_url`, `dot_encode_path`, `parse_bytes_path_url`, `IPv4Address`, `IPv6Address`, and `pytest.raises`.

Control flow: `test_dot_encode_path()` verifies empty, relative, and absolute path encoding. `symmetric_cases` lists URL byte strings that should parse/render round-trip. `test_render_url()` checks every symmetric rendering, invalid relative path with host, escaped host/user cases, `//` path preservation, and dot-encoding when requested. `test_parse_bytes_path_url()` checks auth-required rejection of non-authority forms, invalid schemes/remotes, invalid host text, alternate serialized forms, percent-decoded user/host, SSH URLs, and all symmetric cases.

State and persistence behavior: pure parser/renderer tests with no external state.

Dependencies/integration points: feeds repository remote parsing and command-line URL handling. It integrates Python `ipaddress` objects into bup's byte-oriented URL model.

Risks and test signals: URL grammar has ambiguous forms (`x:`, `x://`, `x:/`, `x:///`) and tests encode the chosen canonical renderings. Signals are structural `URL` equality, exact rendered bytes, and expected `ValueError` or string error for invalid cases.
