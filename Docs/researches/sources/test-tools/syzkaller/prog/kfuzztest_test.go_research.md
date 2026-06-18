# sources/test-tools/syzkaller/prog/kfuzztest_test.go

Purpose: validates KFuzzTest binary argument marshalling.

Important APIs/types/functions: `testCase`, `TestRoundUpPowerOfTwo`, `createBuffer`, `createPrefix`, `TestMarshallKFuzzTestArg`, and `testOne`.

Control flow and state: tests deserialize Linux/amd64 programs, extract a specific arg tree, call `MarshallKFuzztestArg`, independently build expected prefix/region array/relocation table/payload byte slices, split the encoded output by expected lengths, and compare each segment.

Dependencies and integration: uses target deserialization, `encoding/binary`, KFuzzTest constants, and `testify/assert`.

Risks: exact byte arrays are long and sensitive to region ordering, padding, alignment, and kernel format changes. The tests currently cover pointer/group/data/const paths but not unsupported unions or cyclic references beyond visited-region behavior.

Test signals: strong ABI-level checks for magic/version prefix, region counts/offsets/sizes, relocation null/destination IDs, metadata padding, payload alignment, string/data/const serialization, and tail poison padding.
