<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/assert.hpp

## Purpose
This Boost.Assert header defines the assertion macro surface used by Boost and downstream code: `BOOST_ASSERT`, `BOOST_ASSERT_MSG`, `BOOST_VERIFY`, `BOOST_VERIFY_MSG`, and `BOOST_ASSERT_IS_VOID`. It intentionally has no include guard so different assertion policy macros can be changed before reinclusion.

## Important APIs, Types, And Control Flow
The file first undefines prior assertion macros. If `BOOST_DISABLE_ASSERTS` is set, or debug-handler asserts are enabled under `NDEBUG`, assertions expand to `((void)0)` and `BOOST_ASSERT_IS_VOID` is defined. If handler mode is enabled through `BOOST_ENABLE_ASSERT_HANDLER` or debug-handler mode without `NDEBUG`, it includes `boost/config.hpp` and `boost/current_function.hpp`, declares user-provided `boost::assertion_failed` and `boost::assertion_failed_msg`, and routes failed expressions through them with expression text, function, file, and line. Otherwise it delegates to C `assert`.

## State And Persistence
The header has no runtime state of its own. Runtime behavior is controlled entirely by preprocessor state and by a user-supplied handler implementation when handler mode is selected.

## Dependencies And Integration Points
It depends on Boost.Config for `BOOST_LIKELY`/`BOOST_NORETURN`, Boost.CurrentFunction for function names, or `<assert.h>` for default behavior. It integrates broadly with Boost headers and mergerfs C++ code as a policy layer over C assertions.

## Risks And Test Signals
The no-guard design is intentional but risky if a translation unit expects stable macro definitions after later includes. Handler mode requires exactly matching user-defined functions or link failures occur. Test signals are preprocessor/compile tests under `NDEBUG`, `BOOST_DISABLE_ASSERTS`, `BOOST_ENABLE_ASSERT_HANDLER`, `BOOST_ENABLE_ASSERT_DEBUG_HANDLER`, and default assert mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert.hpp -->
