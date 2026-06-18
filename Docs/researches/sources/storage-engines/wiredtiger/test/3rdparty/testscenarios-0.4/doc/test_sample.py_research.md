# sources/storage-engines/wiredtiger/test/3rdparty/testscenarios-0.4/doc/test_sample.py

Purpose: minimal unittest sample used by the documentation tree.

Important APIs, types, and functions: imports `unittest`; defines `TestSample(unittest.TestCase)` with `test_so_easy()` as a no-op passing test.

Control flow: unittest discovery instantiates `TestSample("test_so_easy")` and the method returns normally, producing success.

State and persistence: no state and no persistent side effects.

Dependencies and integration points: depends only on Python `unittest`. It may be included in documentation examples and package distributions through `MANIFEST.in`.

Risks and test signals: behavioral risk is negligible. The useful signal is that documentation/discovery wiring can find and run a simple test.
