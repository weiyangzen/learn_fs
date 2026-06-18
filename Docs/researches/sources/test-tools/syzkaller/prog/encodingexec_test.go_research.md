# sources/test-tools/syzkaller/prog/encodingexec_test.go

Purpose: verifies the executor binary format emitted by `encodingexec.go` and decoded by `decodeexec.go`.

Important APIs/types/functions: `TestSerializeForExecRandom`, `TestSerializeForExec`, and `TestSerializeForExecOverflow`.

Control flow and state: random tests generate programs, serialize for exec, decode them, validate call counts, and collect size histograms/stat accounting. Table tests construct expected varint streams from mixed uint64/int/blob elements and compare raw bytes. Selected cases also compare decoded `ExecProg` structs. Overflow tests synthesize programs that approach/exceed copyout command and buffer limits.

Dependencies and integration: uses `binary.AppendVarint`, `gohistogram`, target descriptions, text deserialization, `ExecCallCount`, `DeserializeExec`, and constants from serializer/decoder.

Risks: exact byte expectations are intentionally brittle because they define ABI behavior. Histogram output is diagnostic only. Large generated overflow cases must remain below test runtime/memory limits while exceeding serializer limits.

Test signals: strong byte-level coverage for copyin offsets, struct alignment, varlen arrays, unions, big-endian metadata, bitfields, proc values, special pointers, checksum chunks, call properties, resource copyout/copyin, and size guards.
