"""Internal exception for Result error propagation.

This module is private - never imported by user code.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class _CommandError(Exception):
    """Command handler returned Err(e). Caught only by run() boundary.

    This exception is an implementation detail of the Result contract.
    User code never sees it - only run() catches and handles it.

    Attributes:
        error: The E from Result[None, E]. Must have suitable __str__.
    """

    error: Any  # Any because we don't constrain E at type level
