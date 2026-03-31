from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import Policy


def evaluate_policy(
    db: Session,
    role: str,
    resource: str,
    action: str,
    risk_score: int,
    ip_address: str | None = None,
) -> tuple[str, str]:
    """
    Evaluates access against stored policies.

    Returns:
        (decision, reason) — decision is "ALLOW" or "DENY"
    """
    current_hour = datetime.now(timezone.utc).hour

    # Query all matching policies for this role + resource + action
    # DENY rules are always checked first (deny-first model)
    policies = (
        db.query(Policy)
        .filter(
            Policy.role == role,
            Policy.resource == resource,
            Policy.action == action,
        )
        .order_by(Policy.effect)  # ALLOW comes before DENY alphabetically — we reverse below
        .all()
    )

    if not policies:
        return "DENY", f"No policy found for role={role} resource={resource} action={action}"

    # Separate DENY and ALLOW rules
    deny_rules  = [p for p in policies if p.effect == "DENY"]
    allow_rules = [p for p in policies if p.effect == "ALLOW"]

    # ── Check explicit DENY rules first ───────────────────
    for policy in deny_rules:
        return "DENY", f"Explicit deny policy: {policy.name}"

    # ── Check ALLOW rules with ABAC conditions ─────────────
    for policy in allow_rules:
        # Time-of-day check
        if policy.allowed_hours_start is not None and policy.allowed_hours_end is not None:
            if not (policy.allowed_hours_start <= current_hour < policy.allowed_hours_end):
                return (
                    "DENY",
                    f"Access denied outside allowed hours "
                    f"({policy.allowed_hours_start}:00–{policy.allowed_hours_end}:00 UTC)"
                )

        # Risk score check
        if risk_score > policy.max_risk_score:
            return (
                "DENY",
                f"Risk score {risk_score} exceeds policy maximum {policy.max_risk_score}"
            )

        # All conditions passed — ALLOW
        return "ALLOW", f"Permitted by policy: {policy.name}"

    return "DENY", "No matching allow policy satisfied all conditions"
