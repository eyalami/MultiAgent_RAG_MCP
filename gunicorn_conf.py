import os
from typing import Any


def on_starting(server: Any) -> None:
    if os.getenv("DEBUGPY", "0") != "1":
        return
    try:
        import debugpy

        host = os.getenv("DEBUGPY_HOST", "0.0.0.0")
        port = int(os.getenv("DEBUGPY_PORT", "5678"))
        debugpy.listen((host, port))
        server.log.info(f"debugpy listening on {host}:{port}")
        # Never block master; only optionally wait when running locally
        if os.getenv("DEBUGPY_WAIT", "0") == "1" and os.getenv("ENV", "dev") == "local":
            server.log.info("Waiting for debugger to attach…")
            debugpy.wait_for_client()
    except Exception as e:
        server.log.warning(f"debugpy setup failed: {e}")