# sources/storage-engines/foundationdb/fdbrpc/LinkTest.cpp

`LinkTest.cpp` is a build/link sentinel. It provides a dummy executable `main()` so unresolved symbols from module linkage are caught by the linker instead of being hidden in static or shared library creation.

The only API is `int main() { return 0; }`. There is no meaningful runtime control flow, state, persistence, or dependency surface.

Its integration point is the build system: creating an executable forces full symbol resolution for the module. The file should remain minimal; adding includes or behavior would make link-test failures less focused. The test signal is linker success or failure rather than a FoundationDB unit test.
