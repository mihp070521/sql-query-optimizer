from .analyzer import Issue


class SuggestionEngine:
    """Generate optimization suggestions from issues."""

    def suggest(self, issues: list[Issue]) -> list[str]:
        suggestions = []
        for issue in sorted(issues, key=lambda i: self._severity_order(i.severity)):
            suggestions.append(f"[{issue.severity.upper()}] {issue.rule}: {issue.suggestion}")
        return suggestions

    def _severity_order(self, severity: str) -> int:
        return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(severity, 4)
