# sources/test-tools/fio/lib/num2str.h

Purpose: declares numeric formatting helpers and unit kinds.

Important APIs/types: `enum n2s_unit` values for none, per-second, byte, bit, byte/s, and bit/s; `num2str`; and `bytes2str_simple`.

Control flow/state: callers choose base, prefix family, maximum length, and units, then free `num2str` results. `bytes2str_simple` is non-allocating.

Dependencies/integration: includes fixed-width integers. Used by fio output code.

Risks/test signals: callers must manage allocated strings and provide adequate buffers for simple formatting. Tests should verify all enum values and boundary formatting.
