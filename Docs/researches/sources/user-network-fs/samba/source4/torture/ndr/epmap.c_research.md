# sources/user-network-fs/samba/source4/torture/ndr/epmap.c

Purpose: this file defines a small Samba torture NDR suite for the DCE/RPC endpoint mapper `epm_Map` operation. It verifies that a captured map request decodes enough of the tower/request structure to expose the expected maximum tower count and map tower length.

Important APIs, types, and functions: the exported entry point is `ndr_epmap_suite(TALLOC_CTX *ctx)`. The test depends on generated endpoint mapper bindings from `librpc/gen_ndr/ndr_epmapper.h`. `map_in_check(struct torture_context *tctx, struct epm_Map *r)` asserts `r->in.max_towers == 1`, `r->in.map_tower != NULL`, and `r->in.map_tower->tower_length == 75`. A response fixture and `map_out_check()` exist inside `#if 0`, documenting expected output-side fields such as `*num_towers == 1` and result `0x4b`, but they are not compiled or registered.

Control flow: `map_in_data` holds a captured inbound `epm_Map` payload containing object/handle space, a protocol tower, and a max-towers value. `ndr_epmap_suite()` creates an `epmap` suite and registers a single `NDR_IN` pull-function test for `epm_Map` with `map_in_check()`. The disabled output test is left as source commentary but has no runtime effect.

State and persistence behavior: there is no mutable state or persistence. The suite parses a static byte array under the torture harness and produces only assertion results.

Dependencies and integration points: this test exercises endpoint mapper IDL generated code, especially decoding of embedded tower structures and request-side pointer fields. Endpoint mapper towers are used by DCE/RPC binding discovery, so this fixture is a compact regression check for tower-length and array/pointer handling in generated NDR code.

Risks: coverage is intentionally minimal. The checker contains FIXME comments for object and entry-handle validation, so important fields are parsed but not asserted. The disabled response fixture means output-side `epm_Map` coverage is absent at runtime. Future IDL changes could preserve tower length and max-towers while breaking tower floor contents, object UUIDs, or entry handle decoding without this test catching it.

Test signals: active failures indicate inability to decode the inbound `epm_Map` request, NULL tower decoding, incorrect max-tower count, or incorrect tower length. Passing this test is a narrow signal that request-side endpoint mapper tower framing still matches the fixture.
