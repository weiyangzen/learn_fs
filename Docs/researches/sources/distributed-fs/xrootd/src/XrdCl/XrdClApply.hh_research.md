# sources/distributed-fs/xrootd/src/XrdCl/XrdClApply.hh

Purpose: implements a C++11-era replacement for `std::apply`, expanding tuple elements into function or method calls.

Important APIs/types: `sequence`, recursive `seq_gen`, `tuple_call_impl`, `Apply(FUNC&&, tuple&)`, and method overload `Apply(METH&&, OBJ&, tuple&)` that binds a member function to an object and two placeholders.

Control flow/state: all logic is compile-time template expansion plus moving tuple elements into the callable. There is no runtime persistence. Dependencies are `<functional>` and `<tuple>`. Integration point is the declarative operations layer that stores operation arguments in tuples and invokes handlers uniformly. Risks: the member-function overload is specialized to two placeholders, so it is not a general method apply; moving tuple members consumes argument state; compile errors can be hard to diagnose. Test signals: zero/two/multiple argument expansion, move-only arguments, and method overload arity.
