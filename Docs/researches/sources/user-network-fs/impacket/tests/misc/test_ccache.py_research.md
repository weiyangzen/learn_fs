# sources/user-network-fs/impacket/tests/misc/test_ccache.py

Purpose: Tests Kerberos credential cache loading, Kirbi conversion, and environment-driven cache parsing.

Important APIs, types, and functions: Uses `CCache.loadFile`, `CCache.loadKirbiFile`, `CCache.parseFile`, `CCache.getCredential`, `Credential`, `prettyPrint`, `pytest.mark.skipif`, and `unittest.mock.patch.dict`.

Control flow: Shared `assert_ccache` validates loaded caches. Tests verify nonexistent files, unsupported v1/v2 caches, valid v3/v4 ccache files, Kirbi inputs, absent `KRB5CCNAME`, missing cache paths, and domain/user filtering.

State and persistence behavior: Reads fixture files under `tests/data`; temporarily patches `os.environ` for `KRB5CCNAME`. No writes.

Dependencies and integration points: Integrates Kerberos ccache parser with filesystem fixtures and environment-based credential discovery.

Risks: Fixture paths are relative to the repository working directory. Python 2 skips environment-patching tests due to mock availability.

Test signals: Good signal for ccache format support, error handling, Kirbi conversion, and TGT/TGS selection from environment caches.
