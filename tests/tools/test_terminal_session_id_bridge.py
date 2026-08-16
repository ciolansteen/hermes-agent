from gateway.session_context import (
    get_session_env,
    scoped_current_session_id,
)


class _InspectingEnvironment:
    def __init__(self):
        self.observed_session_id = None

    def execute(self, command, **kwargs):
        self.observed_session_id = get_session_env("HERMES_SESSION_ID")
        return {"returncode": 0, "output": command, "kwargs": kwargs}


def test_foreground_execute_binds_handler_session_id_and_restores_foreign_context():
    from tools.terminal_tool import _execute_foreground_with_session_id

    env = _InspectingEnvironment()
    with scoped_current_session_id("foreign-session"):
        result = _execute_foreground_with_session_id(
            env,
            "hermes verify --json",
            {"timeout": 60, "cwd": "/tmp"},
            "handler-session",
        )
        restored = get_session_env("HERMES_SESSION_ID")

    assert env.observed_session_id == "handler-session"
    assert restored == "foreign-session"
    assert result["returncode"] == 0
    assert result["kwargs"] == {"timeout": 60, "cwd": "/tmp"}


def test_foreground_execute_without_handler_id_preserves_current_context():
    from tools.terminal_tool import _execute_foreground_with_session_id

    env = _InspectingEnvironment()
    with scoped_current_session_id("current-session"):
        _execute_foreground_with_session_id(env, "true", {}, None)
        restored = get_session_env("HERMES_SESSION_ID")

    assert env.observed_session_id == "current-session"
    assert restored == "current-session"
