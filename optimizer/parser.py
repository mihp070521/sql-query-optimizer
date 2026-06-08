import re
from dataclasses import dataclass, field


@dataclass
class ParsedQuery:
    """Parsed SQL query representation."""
    raw: str
    tables: list[str] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    where_clauses: list[str] = field(default_factory=list)
    joins: list[dict[str, str]] = field(default_factory=list)
    has_select_star: bool = False
    has_limit: bool = False
    limit_value: int | None = None
    has_order_by: bool = False
    query_type: str = "SELECT"


class SQLParser:
    """Simple SQL query parser for optimization analysis."""

    def parse(self, sql: str) -> ParsedQuery:
        sql = sql.strip().rstrip(";")
        query = ParsedQuery(raw=sql)

        query.query_type = self._detect_query_type(sql)

        if query.query_type == "SELECT":
            query.tables = self._extract_tables(sql)
            query.columns = self._extract_columns(sql)
            query.has_select_star = self._has_select_star(sql)
            query.where_clauses = self._extract_where(sql)
            query.joins = self._extract_joins(sql)
            query.has_limit = self._has_limit(sql)
            query.limit_value = self._extract_limit(sql)
            query.has_order_by = "ORDER BY" in sql.upper()

        return query

    def _detect_query_type(self, sql: str) -> str:
        return sql.strip().split()[0].upper()

    def _has_select_star(self, sql: str) -> bool:
        return bool(re.search(r"SELECT\s+\*", sql, re.IGNORECASE))

    def _extract_tables(self, sql: str) -> list[str]:
        tables = []
        # FROM clause
        from_match = re.search(r"FROM\s+(\w+(?:\s+\w+)?)", sql, re.IGNORECASE)
        if from_match:
            tables.append(from_match.group(1).split()[0])

        # JOIN clauses
        join_matches = re.findall(r"JOIN\s+(\w+)", sql, re.IGNORECASE)
        tables.extend(join_matches)

        return list(set(tables))

    def _extract_columns(self, sql: str) -> list[str]:
        select_match = re.search(r"SELECT\s+(.+?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return []

        cols_str = select_match.group(1)
        if cols_str.strip() == "*":
            return ["*"]

        columns = []
        for col in cols_str.split(","):
            col = col.strip()
            # Remove aliases
            parts = col.split()
            columns.append(parts[0].strip())

        return columns

    def _extract_where(self, sql: str) -> list[str]:
        where_match = re.search(r"WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)", sql, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return []

        conditions = re.split(r"\s+AND\s+", where_match.group(1), flags=re.IGNORECASE)
        return [c.strip() for c in conditions]

    def _extract_joins(self, sql: str) -> list[dict[str, str]]:
        pattern = r"(LEFT|RIGHT|INNER|CROSS)?\s*JOIN\s+(\w+)\s+ON\s+(.+?)(?=(?:LEFT|RIGHT|INNER|CROSS|WHERE|ORDER|GROUP|LIMIT|$))"
        matches = re.findall(pattern, sql, re.IGNORECASE | re.DOTALL)

        joins = []
        for join_type, table, on_clause in matches:
            joins.append({
                "type": (join_type or "INNER").upper(),
                "table": table,
                "on": on_clause.strip(),
            })
        return joins

    def _has_limit(self, sql: str) -> bool:
        return bool(re.search(r"LIMIT\s+\d+", sql, re.IGNORECASE))

    def _extract_limit(self, sql: str) -> int | None:
        match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
        return int(match.group(1)) if match else None
