from dataclasses import dataclass
from .parser import ParsedQuery, SQLParser


@dataclass
class Issue:
    severity: str  # critical, high, medium, low
    rule: str
    message: str
    suggestion: str


class QueryAnalyzer:
    """Analyze SQL queries for common performance issues."""

    def __init__(self):
        self.parser = SQLParser()

    def analyze(self, sql: str) -> list[Issue]:
        parsed = self.parser.parse(sql)
        issues = []

        issues.extend(self._check_select_star(parsed))
        issues.extend(self._check_missing_limit(parsed))
        issues.extend(self._check_missing_where(parsed))
        issues.extend(self._check_like_prefix(parsed))
        issues.extend(self._check_not_in(parsed))
        issues.extend(self._check_or_in_where(parsed))
        issues.extend(self._check_function_in_where(parsed))
        issues.extend(self._check_implicit_join(parsed))

        return issues

    def _check_select_star(self, q: ParsedQuery) -> list[Issue]:
        if q.has_select_star:
            return [Issue(
                severity="medium",
                rule="select-star",
                message="SELECT * retrieves all columns, including unnecessary ones",
                suggestion="Explicitly list only the columns you need",
            )]
        return []

    def _check_missing_limit(self, q: ParsedQuery) -> list[Issue]:
        if not q.has_limit and q.query_type == "SELECT":
            return [Issue(
                severity="low",
                rule="missing-limit",
                message="Query has no LIMIT clause",
                suggestion="Add LIMIT to prevent accidentally returning millions of rows",
            )]
        return []

    def _check_missing_where(self, q: ParsedQuery) -> list[Issue]:
        if not q.where_clauses and q.query_type == "SELECT":
            return [Issue(
                severity="low",
                rule="missing-where",
                message="SELECT without WHERE clause scans entire table",
                suggestion="Add WHERE clause to filter results and use indexes",
            )]
        return []

    def _check_like_prefix(self, q: ParsedQuery) -> list[Issue]:
        issues = []
        for clause in q.where_clauses:
            if "LIKE" in clause.upper() and clause.strip().endswith("%'"):
                if not clause.strip().endswith("'%"):
                    continue
                if clause.strip().split("LIKE")[-1].strip().startswith("'%"):
                    issues.append(Issue(
                        severity="high",
                        rule="like-prefix-wildcard",
                        message=f"Leading wildcard in LIKE prevents index usage: {clause}",
                        suggestion="Avoid leading % in LIKE patterns, or use full-text search",
                    ))
        return issues

    def _check_not_in(self, q: ParsedQuery) -> list[Issue]:
        issues = []
        for clause in q.where_clauses:
            if "NOT IN" in clause.upper():
                issues.append(Issue(
                    severity="medium",
                    rule="not-in-subquery",
                    message="NOT IN with subquery can be slow and handles NULLs unexpectedly",
                    suggestion="Use NOT EXISTS or LEFT JOIN ... IS NULL instead",
                ))
        return issues

    def _check_or_in_where(self, q: ParsedQuery) -> list[Issue]:
        issues = []
        for clause in q.where_clauses:
            if " OR " in clause.upper():
                issues.append(Issue(
                    severity="medium",
                    rule="or-in-where",
                    message="OR in WHERE clause may prevent index usage",
                    suggestion="Consider using UNION ALL or IN (...) for better index utilization",
                ))
        return issues

    def _check_function_in_where(self, q: ParsedQuery) -> list[Issue]:
        issues = []
        func_patterns = ["UPPER(", "LOWER(", "TRIM(", "DATE(", "YEAR(", "CAST("]
        for clause in q.where_clauses:
            for func in func_patterns:
                if func in clause.upper():
                    issues.append(Issue(
                        severity="high",
                        rule="function-on-indexed-column",
                        message=f"Function on column in WHERE prevents index usage: {func}",
                        suggestion="Apply the function to the comparison value instead of the column",
                    ))
        return issues

    def _check_implicit_join(self, q: ParsedQuery) -> list[Issue]:
        if len(q.tables) > 1 and not q.joins and "WHERE" in q.raw.upper():
            return [Issue(
                severity="high",
                rule="implicit-join",
                message="Implicit join (comma-separated tables in FROM) is error-prone",
                suggestion="Use explicit JOIN ... ON syntax for clarity and correctness",
            )]
        return []
