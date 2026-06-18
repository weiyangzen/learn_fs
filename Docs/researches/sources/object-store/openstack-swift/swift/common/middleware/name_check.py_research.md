# sources/object-store/openstack-swift/swift/common/middleware/name_check.py

Purpose: Rejects account, container, or object paths containing forbidden characters, excessive path length, or forbidden path substrings such as `/.` and `/..`.

Important APIs and control flow: `NameCheckMiddleware` reads `forbidden_chars`, `maximum_length`, and `forbidden_regexp` from config, compiles the regexp when set, registers its config through `register_swift_info`, and logs through the `name_check` route. `check_character`, `check_length`, and `check_regexp` operate on `Request.path_info`. `__call__` wraps the environ in `Request`, returns `HTTPBadRequest` with a specific message on the first failed check, or delegates to the downstream app.

State, dependencies, and integration: State is immutable middleware configuration plus the compiled regex. It depends on `swift.common.swob`, `get_logger`, and the Swift info registry. It is designed to sit early in the proxy pipeline after initial proxy logging.

Risks and test signals: Regex configuration can make otherwise valid Swift names unavailable or impose CPU-heavy matching if poorly chosen. Tests should cover default forbidden characters, disabled regex, custom regex, maximum length boundaries, WSGI `path_info` encoding behavior, and that downstream is not called on rejection.
