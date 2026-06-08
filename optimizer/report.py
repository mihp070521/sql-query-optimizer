from .analyzer import Issue
from .parser import ParsedQuery


class Reporter:
    """Generate formatted reports from analysis results."""

    def text_report(self, sql: str, issues: list[Issue]) -> str:
        lines = ["=== SQL Query Optimization Report ===\n"]
        lines.append(f"Query: {sql[:100]}{'...' if len(sql) > 100 else ''}\n")

        if not issues:
            lines.append("✅ No issues found!\n")
            return "\n".join(lines)

        by_severity = {}
        for issue in issues:
            by_severity.setdefault(issue.severity, []).append(issue)

        for severity in ["critical", "high", "medium", "low"]:
            if severity not in by_severity:
                continue
            lines.append(f"\n{'🔴' if severity in ('critical','high') else '🟡'} {severity.upper()} ({len(by_severity[severity])})")
            for issue in by_severity[severity]:
                lines.append(f"  • [{issue.rule}] {issue.message}")
                lines.append(f"    → {issue.suggestion}")

        return "\n".join(lines)

    def json_report(self, sql: str, issues: list[Issue]) -> dict:
        return {
            "query": sql,
            "total_issues": len(issues),
            "by_severity": {
                s: len([i for i in issues if i.severity == s])
                for s in ["critical", "high", "medium", "low"]
            },
            "issues": [
                {
                    "severity": i.severity,
                    "rule": i.rule,
                    "message": i.message,
                    "suggestion": i.suggestion,
                }
                for i in issues
            ],
        }
